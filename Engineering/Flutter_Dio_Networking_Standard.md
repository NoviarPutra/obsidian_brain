---
tags:
  - engineering/mobile
  - flutter
  - networking
  - dio
  - architecture
title: "Flutter Dio Networking Standard: Lifecycle, Timeouts & Error Resilience"
---

# Flutter Dio Networking Standard: Lifecycle, Timeouts & Error Resilience

> **Source**: Flutter Production Engineering Standards  
> **Target Persona**: `builder-mobile`, `reviewer`  
> **Core Mandate**: Resilient Networking, Explicit Timeouts, Lifecycle Cancellation (`CancelToken`), Centralized Error Normalization, Zero Interceptor Leaks, and Anti-Retry-Storms.

---

## 1. Core Architecture & Client Lifecycle

Semua panggilan HTTP/REST di Flutter wajib melalui instance `Dio` yang terkonfigurasi secara terpusat. Dilarang membuat instance `Dio` ad-hoc di dalam UI widgets atau local functions.

### A. Base Configuration & Strict Timeouts
Instansiasi `Dio` wajib menetapkan timeout eksplisit pada ketiga fase transmisi. Nilai default tanpa timeout adalah **anti-pattern berat** yang menyebabkan thread menggantung (*hanging requests*) pada koneksi seluler buruk.

```dart
class NetworkConfig {
  static const Duration connectTimeout = Duration(seconds: 15);
  static const Duration receiveTimeout = Duration(seconds: 15);
  static const Duration sendTimeout = Duration(seconds: 15);
}

Dio createDioClient({required String baseUrl, List<Interceptor>? interceptors}) {
  final dio = Dio(
    BaseOptions(
      baseUrl: baseUrl,
      connectTimeout: NetworkConfig.connectTimeout,
      receiveTimeout: NetworkConfig.receiveTimeout,
      sendTimeout: NetworkConfig.sendTimeout,
      headers: <String, dynamic>{
        'Accept': 'application/json',
        'Content-Type': 'application/json; charset=UTF-8',
      },
      responseType: ResponseType.json,
    ),
  );

  // Pasang interceptor terstandarisasi
  if (interceptors != null) {
    dio.interceptors.addAll(interceptors);
  }

  return dio;
}
```

---

## 2. Request Cancellation Lifecycle (`CancelToken`)

> ⚠️ **CRITICAL DOCTRINE**: Setiap HTTP request yang dipicu oleh lifecycle layar/widget **WAJIB** menerima `CancelToken` opsional atau terikat pada lifecycle controller/provider.
>
> Jika user meninggalkan screen (pop route / back) saat request sedang berjalan, request harus dibatalkan seketika untuk mencegah *memory leaks, CPU/battery waste, dan unmounted state mutations*.

### A. Pola Integrasi Riverpod (`AutoDisposeRef`)
Pada Riverpod, pembatalan request terikat otomatis dengan pembersihan provider via `ref.onDispose`:

```dart
@riverpod
Future<List<Transaction>> fetchTransactions(FetchTransactionsRef ref) async {
  final cancelToken = CancelToken();
  ref.onDispose(cancelToken.cancel); // Batal seketika saat route ditutup

  final dio = ref.watch(dioClientProvider);
  try {
    final response = await dio.get(
      '/transactions',
      cancelToken: cancelToken,
    );
    return (response.data as List).map((json) => Transaction.fromJson(json)).toList();
  } on DioException catch (e) {
    if (CancelToken.isCancel(e)) {
      // Pembatalan disengaja karena navigasi, abaikan atau return empty
      return <Transaction>[];
    }
    throw AppNetworkException.fromDioException(e);
  }
}
```

### B. Pola Integrasi GetX (`GetxController.onClose`)
Pada GetX, simpan referensi `CancelToken` di dalam controller dan batalkan di `onClose()`:

```dart
class TransactionController extends GetxController {
  final CancelToken _cancelToken = CancelToken();

  Future<void> loadData() async {
    try {
      final data = await transactionRepository.getTransactions(cancelToken: _cancelToken);
      // mutasi state
    } on DioException catch (e) {
      if (CancelToken.isCancel(e)) return;
      // tangani error
    }
  }

  @override
  void onClose() {
    _cancelToken.cancel('TransactionController disposed');
    super.onClose();
  }
}
```

---

## 3. Centralized Error Normalization (`AppNetworkException`)

Dilarang membiarkan raw `DioException` bocor ke lapisan UI presentation. Seluruh network exceptions wajib dinormalisasi menjadi domain exception yang ber-tipe kuat dan aman ditampilkan ke user.

```dart
enum NetworkErrorType {
  timeout,
  noInternet,
  unauthorized,
  forbidden,
  notFound,
  conflict,
  serverError,
  clientCancelled,
  unknown,
}

class AppNetworkException implements Exception {
  const AppNetworkException({
    required this.type,
    required this.message,
    this.statusCode,
    this.rawError,
  });

  final NetworkErrorType type;
  final String message;
  final int? statusCode;
  final dynamic rawError;

  factory AppNetworkException.fromDioException(DioException dioError) {
    if (CancelToken.isCancel(dioError)) {
      return AppNetworkException(
        type: NetworkErrorType.clientCancelled,
        message: 'Request was cancelled.',
        rawError: dioError,
      );
    }

    switch (dioError.type) {
      case DioExceptionType.connectionTimeout:
      case DioExceptionType.sendTimeout:
      case DioExceptionType.receiveTimeout:
        return AppNetworkException(
          type: NetworkErrorType.timeout,
          message: 'Connection timed out. Please check your internet connection.',
          rawError: dioError,
        );
      case DioExceptionType.connectionError:
        return AppNetworkException(
          type: NetworkErrorType.noInternet,
          message: 'No internet connection detected.',
          rawError: dioError,
        );
      case DioExceptionType.badResponse:
        final code = dioError.response?.statusCode;
        final serverMessage = dioError.response?.data is Map 
            ? (dioError.response?.data['message'] ?? dioError.message)
            : dioError.message;

        if (code == 401) {
          return AppNetworkException(
            type: NetworkErrorType.unauthorized,
            message: serverMessage ?? 'Unauthorized session.',
            statusCode: code,
          );
        } else if (code == 403) {
          return AppNetworkException(
            type: NetworkErrorType.forbidden,
            message: serverMessage ?? 'Access forbidden.',
            statusCode: code,
          );
        } else if (code == 404) {
          return AppNetworkException(
            type: NetworkErrorType.notFound,
            message: serverMessage ?? 'Resource not found.',
            statusCode: code,
          );
        } else if (code != null && code >= 500) {
          return AppNetworkException(
            type: NetworkErrorType.serverError,
            message: 'Server error occurred. Please try again later.',
            statusCode: code,
          );
        }
        return AppNetworkException(
          type: NetworkErrorType.unknown,
          message: serverMessage ?? 'Unexpected network response.',
          statusCode: code,
        );
      default:
        return AppNetworkException(
          type: NetworkErrorType.unknown,
          message: dioError.message ?? 'An unexpected network error occurred.',
          rawError: dioError,
        );
    }
  }

  @override
  String toString() => 'AppNetworkException($type, code: $statusCode, message: $message)';
}
```

---

## 4. Anti-Retry-Storms & Safe Interceptors

1. **Idempotency Guard**:
   - Hanya operasi idempoten (`GET`, `HEAD`, `OPTIONS`, atau `PUT` dengan idempotency key) yang diizinkan untuk di-retry secara otomatis saat network timeout/glitch.
   - Operasi `POST` atau pembayaran mutasi finansial **DILARANG KERAS** di-retry otomatis tanpa idempotency key eksplisit dari backend.
2. **Exponential Backoff with Jitter**:
   - Jika menerapkan retry interceptor, wajib menggunakan exponential backoff dengan random jitter untuk mencegah thundering herd problem pada server:
     $$\text{Delay} = \min(\text{maxDelay}, \text{baseDelay} \times 2^{\text{attempt}} + \text{jitter})$$
   - Maksimum retry: 2-3 kali. Jangan pernah melakukan retry tak terbatas (*infinite retry loops*).
3. **Interceptor Hygiene**:
   - Dilarang membuat *stateful interceptors* yang menyimpan state request di dalam variabel instance global.
   - Interceptor authentication wajib menangani token refresh queue agar multiple concurrent requests tidak memicu multiple duplicate refresh token calls.

---

## 5. Reviewer Audit Checklist for Networking

Sebelum kode networking disetujui untuk production, `reviewer` wajib memvalidasi:

1. [ ] **Timeouts**: `BaseOptions` memiliki konfigurasi eksplisit untuk `connectTimeout`, `receiveTimeout`, dan `sendTimeout`.
2. [ ] **Cancellation**: Method repository/service menerima `CancelToken` dan UI/controller mengikat pembatalan pada lifecycle unmount (`ref.onDispose` atau `onClose`).
3. [ ] **No Raw DioException in UI**: Error ditangkap di lapisan repository dan dinormalisasi menjadi domain exception terstruktur.
4. [ ] **Idempotent Retry Only**: Retry otomatis tidak pernah diaplikasikan pada mutasi `POST` tanpa idempotency headers.
5. [ ] **No Secret Leakage in Logs**: Logging interceptor (seperti `LogInterceptor` / `talker_dio_logger`) tidak mempublikasikan token `Authorization`, password, atau data sensitif pengguna.
