# iOS Wrapper (WKWebView)

Blueprint de um app nativo mínimo que encapsula a PWA `3 Coisas de Hoje` quando precisarmos publicar na App Store (equivalente ao TWA no Android).

## Estrutura sugerida

```
ios-wrapper/
└── ThreeCoisasPWA/
    ├── AppDelegate.swift
    ├── SceneDelegate.swift
    ├── WebViewController.swift
    ├── Assets.xcassets (ícones compatíveis com o manifest)
    ├── LaunchScreen.storyboard (ou SwiftUI)
    └── Info.plist
```

### WebViewController.swift (resumo)

```swift
import UIKit
import WebKit

final class WebViewController: UIViewController, WKUIDelegate, WKNavigationDelegate {
    private let baseURL = URL(string: "https://seu-dominio.com")!
    private lazy var webView: WKWebView = {
        let config = WKWebViewConfiguration()
        config.allowsInlineMediaPlayback = true
        config.defaultWebpagePreferences.preferredContentMode = .mobile
        config.userContentController.add(self, name: "nativeBridge")
        let view = WKWebView(frame: .zero, configuration: config)
        view.uiDelegate = self
        view.navigationDelegate = self
        view.allowsBackForwardNavigationGestures = true
        return view
    }()
    private var refreshControl = UIRefreshControl()

    override func viewDidLoad() {
        super.viewDidLoad()
        view = webView
        refreshControl.addTarget(self, action: #selector(reloadPage), for: .valueChanged)
        webView.scrollView.refreshControl = refreshControl
        loadInitialURL()
    }

    @objc private func reloadPage() {
        webView.reload()
    }

    private func loadInitialURL(path: String? = nil) {
        var components = URLComponents(url: baseURL, resolvingAgainstBaseURL: false)!
        components.path = path ?? "/"
        if components.queryItems == nil {
            components.queryItems = [URLQueryItem(name: "source", value: "ios-wrapper")]
        }
        webView.load(URLRequest(url: components.url!))
    }

    func webView(_ webView: WKWebView, decidePolicyFor navigationAction: WKNavigationAction,
                 decisionHandler: @escaping (WKNavigationActionPolicy) -> Void) {
        guard let url = navigationAction.request.url else {
            decisionHandler(.cancel)
            return
        }
        if url.host == baseURL.host {
            decisionHandler(.allow)
        } else {
            decisionHandler(.cancel)
            let safariVC = SFSafariViewController(url: url)
            present(safariVC, animated: true)
        }
    }
}
```

## Capabilities obrigatórias

1. **App Transport Security (ATS)** – permitir apenas HTTPS.
2. **Background Modes > Remote notifications** (se for encaminhar push da PWA).
3. **Associated Domains** para `applinks:seu-dominio.com` (Universal Links).
4. **Push Notifications** + chave APNs se decidirmos reenviar notificações.

## apple-app-site-association

Disponibilize em `https://seu-dominio.com/.well-known/apple-app-site-association`:

```json
{
  "applinks": {
    "details": [{
      "appID": "TEAMID.com.suaempresa.ThreeCoisasPWA",
      "paths": ["/", "/historico/*", "/revisao/*"]
    }]
  }
}
```

## Ícones e launch screen

- Reaproveitar os PNGs do manifest (`icon-192`, `icon-512`, `apple-touch-icon`).
- Launch screen estática (background `#0f172a`, logo central).

## Build & testes

1. `cd ios-wrapper && open ThreeCoisasPWA.xcodeproj`.
2. Configure o `Bundle Identifier` e a equipe (`Signing & Capabilities`).
3. Ajuste `baseURL` para o domínio final (HTTPS).
4. Rode `Cmd + R` no simulador; verifique login, navegação, offline.
5. Para deep links, execute `xcrun simctl openurl booted https://seu-dominio.com/historico/`.

## Boas práticas

- Habilite `WKWebsiteDataStore.default().removeData` no menu “Limpar cache”.
- Registre `navigator.serviceWorker` normalmente dentro da PWA; o wrapper apenas projeta o WebView.
- Quando o app abrir por Universal Link, passe o caminho para `loadInitialURL(path:)`.
- Utilize `NSUserDefaults` + `WKUserContentController` para compartilhar estado leve (opcional).

> **Nota:** Este wrapper não duplica lógica de negócio. Toda autenticação, push (via Web Push) e armazenamento continuam dentro da PWA.

