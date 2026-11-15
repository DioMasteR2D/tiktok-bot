package com.diomaster.freellmapi;

import android.app.Activity;
import android.os.Bundle;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.webkit.WebResourceRequest;
import android.widget.LinearLayout;
import android.widget.Button;
import android.widget.TextView;
import android.view.ViewGroup;

public class MainActivity extends Activity {
  WebView browser;
  @Override public void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);
    LinearLayout root = new LinearLayout(this); root.setOrientation(LinearLayout.VERTICAL);
    TextView info = new TextView(this);
    info.setText("FreeLLMAPI • Το API πρέπει να τρέχει στο Termux. Dashboard: localhost:5173");
    info.setPadding(16,16,16,16);
    root.addView(info);
    Button refresh = new Button(this); refresh.setText("Άνοιγμα / Ανανέωση dashboard");
    root.addView(refresh);
    browser = new WebView(this); browser.getSettings().setJavaScriptEnabled(true);
    browser.getSettings().setDomStorageEnabled(true);
    browser.setWebViewClient(new WebViewClient() {
      @Override public void onReceivedError(WebView view, WebResourceRequest request, android.webkit.WebResourceError error) {
        if (request.isForMainFrame()) info.setText("Δεν βρέθηκε ο τοπικός server. Εκκίνησε πρώτα το FreeLLMAPI στο Termux (npm run dev).");
      }
      @Override public void onPageFinished(WebView view, String url) { if(url.startsWith("http://localhost:5173")) info.setText("FreeLLMAPI • Τοπικό dashboard"); }
    });
    root.addView(browser, new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,0,1));
    refresh.setOnClickListener(v -> browser.loadUrl("http://localhost:5173"));
    setContentView(root);
    browser.loadUrl("http://localhost:5173");
  }
  @Override public void onBackPressed() { if(browser.canGoBack()) browser.goBack(); else super.onBackPressed(); }
}
