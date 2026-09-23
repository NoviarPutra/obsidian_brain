---
tags:
  - engineering/mobile
  - flutter
  - riverpod
  - state-management
  - architecture
title: "Flutter Riverpod v2.x/v3.x Architecture, Performance & Anti-Memory-Leak Standard"
---

# Flutter Riverpod v2.x/v3.x Architecture, Performance & Anti-Memory-Leak Standard

> **Source**: https://riverpod.dev/docs/introduction/getting_started (v2.x & v3.x)  
> **Target Persona**: `builder-mobile`, `reviewer`  
> **Core Mandate**: Best Practice, Zero Over-Engineering, Robust, Bullet-Proof, Future-Proof, Anti-Memory Leak, 60 FPS Rebuild Precision, and Clean GoRouter Integration.

---

## 1. Core Architecture & Mental Model

Riverpod adalah reactive caching and state-management framework yang compile-safe, unidirectional, dan terisolasi dari widget tree Flutter (`BuildContext` independent).

### A. Root Initialization: `ProviderScope`
Setiap aplikasi Flutter berbasis Riverpod **wajib** dibungkus oleh `ProviderScope` di titik paling atas (`main.dart`).

```dart
void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(
    const ProviderScope(
      child: MyApp(),
    ),
  );
}
```

Jika digabungkan dengan `flutter_screenutil_plus` dan `go_router`:
```dart
class MyApp extends ConsumerWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final router = ref.watch(routerProvider);

    return ScreenUtilPlusInit(
      designSize: const Size(390, 844),
      minTextAdapt: true,
      builder: (context, child) {
        return MaterialApp.router(
          routerConfig: router,
          title: 'Production App',
        );
      },
    );
  }
}
```

---

## 2. Dual Provider Standard: Pragmatic Codegen vs. Lean Manual

`builder-mobile` wajib menguasai kedua paradigma dan menyesuaikan dengan stack proyek yang sedang dikerjakan tanpa memaksakan dependensi yang belum ada (Prinsip YAGNI).

### A. Paradigma 1: Code Generation (`@riverpod`)
Digunakan jika proyek sudah mengonfigurasi `riverpod_annotation` dan `build_runner`.
- **Karakteristik**: AutoDispose secara default, syntax terstandarisasi, inferensi tipe otomatis.

```dart
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'product_notifier.g.dart';

// 1. Controller / AsyncNotifier (Auto-Disposed by default)
@riverpod
class ProductListNotifier extends _$ProductListNotifier {
  @override
  FutureOr<List<Product>> build() async {
    return _fetchProducts();
  }

  Future<void> refresh() async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() => _fetchProducts());
  }

  Future<List<Product>> _fetchProducts() async {
    final repo = ref.read(productRepositoryProvider);
    return repo.getProducts();
  }
}

// 2. Global Singleton Service (Keep Alive)
@Riverpod(keepAlive: true)
class AuthNotifier extends _$AuthNotifier {
  @override
  AuthState build() => AuthState.initial();
}
```

### B. Paradigma 2: Lean Manual Providers (Zero Codegen / Pure Dart)
Digunakan jika proyek mengutamakan kecepatan build, zero overhead generator, atau tanpa `build_runner`.

```dart
// 1. UI Controller: AutoDisposeAsyncNotifier
final productListProvider = AsyncNotifierProvider.autoDispose<ProductListNotifier, List<Product>>(
  ProductListNotifier.new,
);

class ProductListNotifier extends AutoDisposeAsyncNotifier<List<Product>> {
  @override
  FutureOr<List<Product>> build() async {
    return _fetchProducts();
  }

  Future<void> refresh() async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() => _fetchProducts());
  }

  Future<List<Product>> _fetchProducts() async {
    final repo = ref.read(productRepositoryProvider);
    return repo.getProducts();
  }
}

// 2. Pure Read-Only / Computed Provider
final activeProductsProvider = Provider.autoDispose<List<Product>>((ref) {
  final productsAsync = ref.watch(productListProvider);
  return productsAsync.valueOrNull?.where((p) => p.isActive).toList() ?? [];
});
```

---

## 3. Anti-Memory Leak Doctrine: Strict AutoDispose & Resource Hygiene

> ⚠️ **RULE**: Seluruh controller, view-model, form state, dan data-fetching provider **WAJIB** menggunakan `autoDispose` (atau default pada `@riverpod`).
> 
> Pengecualian hanya untuk **Global App-Wide Singletons** (`AuthNotifier`, `SessionRepository`, `ThemeNotifier`, `AppConfig`) yang memang harus bertahan sepanjang siklus hidup aplikasi.

### A. Lifecycle Disposal Hooks (`ref.onDispose` & `ref.onCancel`)
Jika provider menginisialisasi resources eksternal (Timer, StreamSubscription, WebSocket, atau File Handle), bersihkan selalu via callback `ref.onDispose`:

```dart
final liveLocationProvider = StreamProvider.autoDispose<LocationData>((ref) {
  final locationService = ref.watch(locationServiceProvider);
  final subscription = locationService.stream.listen((data) {
    // Handling
  });

  // Anti-leak guard: batalkan subscription saat provider ter-dispose
  ref.onDispose(() {
    subscription.cancel();
  });

  return locationService.stream;
});
```

### B. Caching dengan Graceful Timeout (`cacheFor`)
Untuk mencegah fetching berulang yang agresif saat navigasi bolak-balik namun tetap membebaskan memori setelah durasi tertentu:

```dart
extension AutoDisposeRefExtension<T> on AutoDisposeRef<T> {
  void cacheFor(Duration duration) {
    final link = keepAlive();
    final timer = Timer(duration, link.close);
    onDispose(timer.cancel);
  }
}

// Penggunaan pada provider
@riverpod
Future<ProductDetails> productDetails(ProductDetailsRef ref, String id) async {
  ref.cacheFor(const Duration(minutes: 5)); // Mempertahankan cache 5 menit sebelum dilepas dari memori
  return ref.read(repositoryProvider).getDetails(id);
}
```

---

## 4. GoRouter & Riverpod Canonical Bridge: Reactive Redirection

> ⚠️ **CRITICAL DO/DON'T**:
> - ❌ **DILARANG**: Memanggil `ref.watch(authProvider)` di dalam deklarasi factory `GoRouter` yang memicu re-instansiasi `GoRouter` baru setiap auth state berubah. Hal ini **menghancurkan navigation history, memicu flickering, dan mereset scroll position**.
> - ✅ **WAJIB**: `GoRouter` diinisialisasi **satu kali** di dalam `routerProvider`. Gunakan `refreshListenable` untuk memicu evaluasi ulang `redirect` tanpa merombak instance router.

### Implementasi Kanonikal:

```dart
// 1. Auth Change Notifier Bridge
class AuthRefreshNotifier extends ChangeNotifier {
  AuthRefreshNotifier(this._ref) {
    _ref.listen<AuthState>(
      authNotifierProvider,
      (_, __) => notifyListeners(),
    );
  }

  final Ref _ref;
}

final authRefreshNotifierProvider = Provider<AuthRefreshNotifier>((ref) {
  return AuthRefreshNotifier(ref);
});

// 2. Singleton GoRouter Provider
final routerProvider = Provider<GoRouter>((ref) {
  final refreshNotifier = ref.watch(authRefreshNotifierProvider);

  return GoRouter(
    navigatorKey: rootNavigatorKey,
    initialLocation: '/home',
    refreshListenable: refreshNotifier, // Reaktif memicu redirect tanpa rebuild instance router!
    redirect: (BuildContext context, GoRouterState state) {
      // Baca state via ref.read agar tidak merebuild router
      final authState = ref.read(authNotifierProvider);
      final isLoggedIn = authState.isAuthenticated;
      final isLoggingIn = state.matchedLocation == '/login';
      final isPublic = state.matchedLocation == '/splash';

      // Anti-infinite redirect loop guard
      if (!isLoggedIn && !isLoggingIn && !isPublic) {
        return '/login?from=${Uri.encodeComponent(state.uri.toString())}';
      }
      if (isLoggedIn && isLoggingIn) {
        return '/home';
      }
      return null;
    },
    routes: <RouteBase>[
      // Rute-rute aplikasi
    ],
  );
});
```

---

## 5. 60 FPS Rebuild Precision: `ref.watch` vs. `select` vs. `Consumer`

Untuk menjamin performa render 60 FPS dan meniadakan layout thrashing:

### A. Surgical Property Watching dengan `.select()`
Hindari me-rebuild widget besar jika hanya satu properti kecil dari objek yang berubah:

```dart
// ❌ Suboptimal: Widget rebuild setiap kali ADA field apa pun pada UserProfile yang berubah
final user = ref.watch(userProfileProvider);
return Text(user.displayName);

// ✅ Best Practice: Rebuild HANYA saat `displayName` berubah
final displayName = ref.watch(userProfileProvider.select((user) => user.displayName));
return Text(displayName);
```

### B. Batasi Scope Rebuild dengan Leaf `Consumer`
Jangan ubah seluruh screen menjadi `ConsumerWidget` jika hanya satu icon atau teks yang reaktif:

```dart
class HeavyDashboardScreen extends StatelessWidget {
  const HeavyDashboardScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Dashboard'),
        actions: [
          // Rebuild terisolasi hanya pada badge notifikasi
          Consumer(
            builder: (context, ref, child) {
              final unreadCount = ref.watch(unreadNotificationCountProvider);
              return Badge(label: Text('$unreadCount'), child: child!);
            },
            child: const Icon(Icons.notifications), // child statis tidak direbuild
          ),
        ],
      ),
      body: const HeavyComplexStaticWidget(), // Tidak pernah ter-rebuild!
    );
  }
}
```

### C. Ref Consumption Rules
1. **`ref.watch`**: Hanya di dalam method `build()` widget atau body provider.
2. **`ref.read`**: Hanya di dalam event callbacks (`onPressed`, `onTap`) atau method controller. Dilarang di dalam `build()` method karena tidak reaktif.
3. **`ref.listen`**: Untuk UI side-effects yang tidak merender data secara visual (misal: memunculkan `SnackBar`, dialog error, atau analitik).

```dart
// Side-effect listening di dalam build:
ref.listen<AsyncValue<void>>(checkoutControllerProvider, (previous, next) {
  next.whenOrNull(
    error: (err, stack) => ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(err.toString())),
    ),
  );
});
```

---

## 6. Robust Async Handling: `AsyncValue` & Mutation Lifecycle

Riverpod menyediakan tipe data `AsyncValue<T>` yang mengeliminasi boilerplate flag `isLoading`, `errorMessage`, dan `data`.

### A. Safe Pattern Matching via `.when()`
```dart
@override
Widget build(BuildContext context, WidgetRef ref) {
  final productsAsync = ref.watch(productListProvider);

  return productsAsync.when(
    data: (products) => ListView.builder(
      itemCount: products.length,
      itemBuilder: (context, i) => ProductCard(product: products[i]),
    ),
    loading: () => const Center(child: CircularProgressIndicator.adaptive()),
    error: (error, stack) => ErrorStateView(
      message: error.toString(),
      onRetry: () => ref.read(productListProvider.notifier).refresh(),
    ),
  );
}
```

### B. Safe Mutations with `AsyncValue.guard()`
Hindari blok `try-catch` repetitif di dalam controller:

```dart
Future<void> submitOrder(OrderPayload payload) async {
  state = const AsyncValue.loading();
  // AsyncValue.guard otomatis menangkap exception dan mengonversinya menjadi AsyncValue.error
  state = await AsyncValue.guard(() => _orderService.submit(payload));
}
```

---

## 7. Dependency Injection & Unit Testing Hygiene

Riverpod mempermudah pengujian unit murni tanpa membutuhkan runtime Flutter UI atau mocking context.

### A. Unit Testing Provider via `ProviderContainer`
```dart
void main() {
  test('ProductListNotifier updates state with fetched products', () async {
    final mockRepo = MockProductRepository();
    when(() => mockRepo.getProducts()).thenAnswer((_) async => [Product(id: '1', name: 'Shoes')]);

    final container = ProviderContainer(
      overrides: [
        productRepositoryProvider.overrideWithValue(mockRepo),
      ],
    );
    addTearDown(container.dispose); // Clean hygiene

    // Validasi pembacaan state
    expect(
      container.read(productListProvider),
      const AsyncValue<List<Product>>.loading(),
    );

    // Tunggu evaluasi async selesai
    final result = await container.read(productListProvider.future);
    expect(result.length, 1);
    expect(result.first.name, 'Shoes');
  });
}
```

---

## 8. Dual-Axis Reviewer Checklist for Riverpod

Sebelum kode di-merge ke production, `reviewer` dan `builder-mobile` wajib memvalidasi checklist berikut:

1. [ ] **AutoDispose Compliance**: Seluruh UI controller/view-model menggunakan `autoDispose` (atau `@riverpod` default). Tidak ada controller lokal yang berumur kekal tanpa alasan valid.
2. [ ] **Resource Cleanup**: Timer, Stream, dan WebSocket dibersihkan di dalam callback `ref.onDispose`.
3. [ ] **GoRouter Isolation**: `GoRouter` tidak di-rebuild via `ref.watch(authProvider)`. Navigasi menggunakan `refreshListenable` bridge.
4. [ ] **No `ref.read` in Build**: Tidak ada pemanggilan `ref.read` di dalam widget `build()` method.
5. [ ] **No `ref.watch` in Callbacks**: Tidak ada pemanggilan `ref.watch` di dalam button `onPressed` atau fungsi handler.
6. [ ] **Rebuild Minimization**: Widget kompleks menggunakan `.select()` untuk membatasi rebuild hanya pada property spesifik, atau menggunakan leaf `Consumer`.
7. [ ] **AsyncValue Safety**: Penanganan state asinkron menggunakan `.when()` atau `.maybeWhen()`, dan mutasi menggunakan `AsyncValue.guard()`.
8. [ ] **Zero Over-Engineering**: Tidak ada layer perantara/wrapper yang tidak dibutuhkan (YAGNI). Provider didefinisikan langsung pada domain terkait.
