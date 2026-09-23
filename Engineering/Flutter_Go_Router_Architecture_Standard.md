---
tags:
  - engineering/mobile
  - flutter
  - navigation
  - routing
  - architecture
title: "Flutter GoRouter v18+ Declarative Architecture & Performance Standard"
---

# Flutter GoRouter v18+ Declarative Architecture & Performance Standard

> **Source**: https://pub.dev/packages/go_router (v18.0.1+)  
> **Target Persona**: `builder-mobile`, `reviewer`  
> **Core Mandate**: Declarative Routing, Multi-Stack State Preservation (`StatefulShellRoute`), Zero Memory Leaks, Safe Deep Linking, Type-Safe Contracts, and Clean State Integration (Riverpod / GetX).

---

## 1. Core Architecture & Mental Model

`go_router` adalah declarative routing engine resmi untuk Flutter yang dibangun di atas Router API (Navigator 2.0). Paket ini menggantikan routing imperatif tradisional (`Navigator.push`) dengan URL-driven routing yang sinkron secara native dengan platform web, Android back button, dan mobile deep links.

### A. Imperative vs. Declarative Navigation
- **`context.go('/path')` (Declarative)**:
  - Mengubah seluruh routing stack agar sesuai dengan hierarki path URL yang dituju.
  - Wajib digunakan untuk perpindahan antar screen utama, link eksternal/deep link, dan pergantian fitur.
  - URL di address bar (Web) otomatis diperbarui.
- **`context.push('/path')` (Imperative)**:
  - Mendorong page baru ke atas Navigator stack yang sedang aktif tanpa merombak hierarki stack di bawahnya.
  - Mengembalikan `Future<T?>` untuk menerima return value saat page di-pop:
    ```dart
    final result = await context.push<bool>('/edit-profile');
    if (result == true) {
      // Refresh data
    }
    ```
- **`context.pop([result])`**:
  - Menutup screen teratas dan mengembalikan result ke pemanggil.
- **`context.replace('/path')`**:
  - Mengganti rute teratas saat ini dengan rute baru tanpa menambah kedalaman stack.

### B. Root Router Setup
Selalu hubungkan `GoRouter` melalui `MaterialApp.router`:

```dart
final GoRouter appRouter = GoRouter(
  navigatorKey: rootNavigatorKey,
  initialLocation: '/',
  debugLogDiagnostics: kDebugMode,
  routes: <RouteBase>[
    // Route tree definitions
  ],
  errorBuilder: (context, state) => NotFoundScreen(error: state.error),
);

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return ScreenUtilPlusInit(
      designSize: const Size(390, 844),
      minTextAdapt: true,
      builder: (context, child) {
        return MaterialApp.router(
          routerConfig: appRouter,
          title: 'Production Flutter App',
        );
      },
    );
  }
}
```

---

## 2. Multi-Tab Bottom Navigation: `StatefulShellRoute.indexedStack`

> ⚠️ **RULE**: DILARANG KERAS menggunakan `ShellRoute` biasa untuk Bottom Navigation Bar pada aplikasi produksi. `ShellRoute` membuang state (scroll position, form inputs, controller state) setiap kali user berpindah tab.
> 
> Gunakan **`StatefulShellRoute.indexedStack`** yang memelihara independent `Navigator` stack terisolasi untuk tiap branch.

### Implementasi Kanonikal Multi-Branch:

```dart
final GlobalKey<NavigatorState> rootNavigatorKey = GlobalKey<NavigatorState>(debugLabel: 'root');

final StatefulShellRoute bottomNavRoute = StatefulShellRoute.indexedStack(
  builder: (BuildContext context, GoRouterState state, StatefulNavigationShell navigationShell) {
    return MainScaffoldWithNavBar(navigationShell: navigationShell);
  },
  branches: <StatefulShellBranch>[
    // Tab 1: Dashboard / Home
    StatefulShellBranch(
      routes: <RouteBase>[
        GoRoute(
          path: '/home',
          name: 'home',
          builder: (context, state) => const HomeScreen(),
          routes: <RouteBase>[
            GoRoute(
              path: 'details/:id',
              name: 'home-details',
              builder: (context, state) => DetailsScreen(id: state.pathParameters['id']!),
            ),
          ],
        ),
      ],
    ),

    // Tab 2: Activity / Feeds
    StatefulShellBranch(
      routes: <RouteBase>[
        GoRoute(
          path: '/activity',
          name: 'activity',
          builder: (context, state) => const ActivityScreen(),
        ),
      ],
    ),

    // Tab 3: Profile & Settings
    StatefulShellBranch(
      routes: <RouteBase>[
        GoRoute(
          path: '/profile',
          name: 'profile',
          builder: (context, state) => const ProfileScreen(),
        ),
      ],
    ),
  ],
);
```

### Scaffold Consumer & Tab Switch Logic:
```dart
class MainScaffoldWithNavBar extends StatelessWidget {
  const MainScaffoldWithNavBar({
    required this.navigationShell,
    super.key,
  });

  final StatefulNavigationShell navigationShell;

  void _onTap(int index) {
    // initialLocation: true akan mereset branch ke rute awal jika tab yang sama ditekan ulang
    navigationShell.goBranch(
      index,
      initialLocation: index == navigationShell.currentIndex,
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: navigationShell,
      bottomNavigationBar: NavigationBar(
        selectedIndex: navigationShell.currentIndex,
        onDestinationSelected: _onTap,
        destinations: const <NavigationDestination>[
          NavigationDestination(icon: Icon(Icons.home_outlined), label: 'Home'),
          NavigationDestination(icon: Icon(Icons.show_chart), label: 'Activity'),
          NavigationDestination(icon: Icon(Icons.person_outline), label: 'Profile'),
        ],
      ),
    );
  }
}
```

---

## 3. Modal & Full-Screen Overlay via `parentNavigatorKey`

Ketika screen atau modal dialog harus menutupi seluruh layar (termasuk menutupi `BottomNavigationBar` milik `StatefulShellRoute`), konfigurasikan `parentNavigatorKey: rootNavigatorKey`:

```dart
GoRoute(
  path: '/checkout',
  name: 'checkout',
  parentNavigatorKey: rootNavigatorKey, // Menutupi Shell navigation dan BottomBar
  builder: (context, state) => const FullscreenCheckoutScreen(),
);
```

---

## 4. Parameter Handling: Path, Query, and Extra

| Tipe Parameter | Sintaks Deklarasi | Sintaks Akses | Karakteristik Web & Deep Link |
|---|---|---|---|
| **Path Parameter** | `/order/:orderId` | `state.pathParameters['orderId']!` | ✅ Preserved pada refresh & deep link |
| **Query Parameter** | `/search` | `state.uri.queryParameters['q']` | ✅ Preserved pada refresh & deep link |
| **Extra Object** | N/A (Object payload) | `state.extra as TransactionModel?` | ❌ **Hilang saat Web refresh / Direct deep link** |

### Aturan Emas Parameter:
1. **Identifier Primer Wajib di URL**: Gunakan `pathParameters` untuk ID resource (misal: `/invoices/:id`).
2. **Defensive Guard pada `extra`**: Jika screen mengonsumsi `state.extra`, selalu sertakan fallback fetching via repository menggunakan ID dari `pathParameters` untuk mengantisipasi deep link langsung:
   ```dart
   GoRoute(
     path: '/invoices/:id',
     builder: (context, state) {
       final invoiceId = state.pathParameters['id']!;
       final invoice = state.extra as InvoiceModel?;
       return InvoiceDetailScreen(
         invoiceId: invoiceId,
         initialInvoice: invoice, // Jika null, screen akan fetch via invoiceId
       );
     },
   )
   ```

---

## 5. Auth Guards & Redirection Lifecycle

GoRouter menyediakan guard terintegrasi via callback `redirect` yang dievaluasi sebelum navigasi dirender.

### A. Anti-Infinite Loop Pattern
> ⚠️ **CRITICAL**: Evaluasi selalu kondisi tujuan (`matchedLocation`) sebelum mengembalikan redirect path.

```dart
String? authGuardRedirect(BuildContext context, GoRouterState state) {
  final authService = context.read<AuthService>(); // atau ref.read(authProvider)
  final bool isLoggedIn = authService.isAuthenticated;
  final bool isLoggingIn = state.matchedLocation == '/login';
  final bool isPublicRoute = state.matchedLocation == '/splash' || state.matchedLocation == '/onboarding';

  // 1. User belum login dan mencoba akses rute terproteksi -> redirect ke /login
  if (!isLoggedIn && !isLoggingIn && !isPublicRoute) {
    return '/login?from=${Uri.encodeComponent(state.uri.toString())}';
  }

  // 2. User sudah login dan berada di /login -> redirect ke /home
  if (isLoggedIn && isLoggingIn) {
    return '/home';
  }

  // 3. Tidak ada perubahan rute
  return null;
}
```

### B. Reaktifitas via `refreshListenable`
Gunakan `refreshListenable` untuk memicu re-evaluasi router saat auth state berubah secara asinkron tanpa merombak seluruh instance `GoRouter`:

```dart
final GoRouter router = GoRouter(
  refreshListenable: authChangeNotifier,
  redirect: authGuardRedirect,
  routes: [...],
);
```

---

## 6. Type-Safe Routing via `go_router_builder`

Untuk project skala enterprise, utamakan rute bertipe kuat menggunakan generator `go_router_builder`.

### Deklarasi Rute Bertipe:
```dart
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

part 'app_routes.g.dart';

@TypedGoRoute<HomeRoute>(
  path: '/',
  routes: <TypedGoRoute<OrderDetailsRoute>>[
    TypedGoRoute<OrderDetailsRoute>(path: 'order/:orderId'),
  ],
)
class HomeRoute extends GoRouteData {
  const HomeRoute();

  @override
  Widget build(BuildContext context, GoRouterState state) => const HomeScreen();
}

class OrderDetailsRoute extends GoRouteData {
  const OrderDetailsRoute({required this.orderId});

  final String orderId;

  @override
  Widget build(BuildContext context, GoRouterState state) {
    return OrderDetailsScreen(orderId: orderId);
  }
}
```

### Eksekusi Navigasi Type-Safe:
```dart
// Compile-time safe: Tidak ada risiko typo string URL atau query parameter!
const HomeRoute().go(context);
OrderDetailsRoute(orderId: 'ORD-9981').push(context);
```

---

## 7. High-Performance Custom Transitions

Gunakan `pageBuilder` bersama `CustomTransitionPage` untuk animasi 60 FPS yang hardware-accelerated:

```dart
GoRoute(
  path: '/settings',
  pageBuilder: (context, state) => CustomTransitionPage<void>(
    key: state.pageKey, // Menjamin lifecycle preservation
    child: const SettingsScreen(),
    transitionsBuilder: (context, animation, secondaryAnimation, child) {
      // Fade transition hardware-accelerated
      return FadeTransition(
        opacity: CurveTween(curve: Curves.easeInOut).animate(animation),
        child: child,
      );
    },
  ),
);
```

Untuk perpindahan tab instan tanpa lag atau overhead rendering animasi:
```dart
GoRoute(
  path: '/instant-tab',
  pageBuilder: (context, state) => NoTransitionPage<void>(
    key: state.pageKey,
    child: const InstantTabScreen(),
  ),
);
```

---

## 8. State Management Integration (Riverpod & GetX)

### A. Riverpod Standard (Recommended Architecture)
```dart
final routerProvider = Provider<GoRouter>((ref) {
  final authNotifier = ref.watch(authNotifierProvider);

  return GoRouter(
    navigatorKey: rootNavigatorKey,
    initialLocation: '/home',
    refreshListenable: authNotifier,
    redirect: (context, state) {
      final isAuth = authNotifier.isAuthenticated;
      final isLoggingIn = state.matchedLocation == '/login';
      if (!isAuth) return isLoggingIn ? null : '/login';
      if (isLoggingIn) return '/home';
      return null;
    },
    routes: [...],
  );
});
```

### B. GetX Separation of Concerns Standard
> ⚠️ **HARD RULE**: Saat GoRouter digunakan, **DILARANG KERAS** memanggil `Get.to()`, `Get.off()`, atau `Get.back()`. Seluruh navigasi wajib dijalankan lewat `context.go()`, `context.push()`, dan `context.pop()`.
>
> GetX difokuskan murni sebagai State Management (`GetxController`, `Obx`, `Get.put()`).

```dart
GoRoute(
  path: '/wallet',
  builder: (context, state) {
    // Inisialisasi controller secara aman terikat pada widget lifecycle
    final controller = Get.put(WalletController());
    return WalletScreen(controller: controller);
  },
);
```

---

## 9. Defensive SRE & Production Quality Checklist

Sebelum kode navigasi di-merge ke production, `reviewer` dan `builder-mobile` wajib memvalidasi checklist berikut:

1. [ ] **StatefulShellRoute**: Tab utama menggunakan `StatefulShellRoute.indexedStack` (Bukan `ShellRoute` polos).
2. [ ] **Modal Coverage**: Dialog dan Full-screen modals mengonfigurasi `parentNavigatorKey: rootNavigatorKey`.
3. [ ] **Deep Link Resilient**: Tidak bergantung eksklusif pada `state.extra` tanpa fallback fetching via `pathParameters`.
4. [ ] **Infinite Loop Guard**: Fungsi `redirect` memvalidasi `state.matchedLocation` sebelum mereturn target path.
5. [ ] **PageKey Stability**: Setiap `pageBuilder` mendefinisikan `key: state.pageKey`.
6. [ ] **No Routing Engine Collisions**: Tidak ada pemanggilan navigasi legacy `Navigator.of(context).pushNamed()` atau `Get.to()` di dalam project GoRouter.
7. [ ] **ScreenUtilPlus Harmony**: `ScreenUtilPlusInit` membungkus `MaterialApp.router` secara benar pada root level.
8. [ ] **Automated Testing Coverage**: Navigation flow diverifikasi melalui Widget Tests dengan `tester.pumpAndSettle()`.
