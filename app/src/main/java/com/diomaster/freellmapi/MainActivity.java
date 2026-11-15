package com.diomaster.freellmapi;

import android.app.Activity;
import android.os.Bundle;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.provider.Settings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.webkit.WebResourceRequest;
import android.widget.LinearLayout;
import android.widget.Button;
import android.widget.TextView;
import android.view.ViewGroup;
import android.graphics.Color;
import android.view.Gravity;

public class MainActivity extends Activity {
  private static final String DASHBOARD = "http://localhost:5173";
  private static final String TERMUX = "com.termux";
  private static final int REQUEST_TERMUX_PERMISSION = 741;
  private WebView browser;
  private TextView info;
  private Button startButton;

  @Override public void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);
    LinearLayout root = new LinearLayout(this);
    root.setOrientation(LinearLayout.VERTICAL);
    root.setPadding(18, 18, 18, 10);
    root.setBackgroundColor(Color.rgb(15, 23, 42));

    TextView title = new TextView(this);
    title.setText("FreeLLMAPI");
    title.setTextColor(Color.WHITE);
    title.setTextSize(25);
    title.setGravity(Gravity.CENTER_VERTICAL);
    root.addView(title);

    info = new TextView(this);
    info.setTextColor(Color.LTGRAY);
    info.setText("Πάτησε «Εκκίνηση» για να ξεκινήσει το FreeLLMAPI στο Termux.");
    info.setPadding(0, 12, 0, 12);
    root.addView(info);

    startButton = new Button(this);
    startButton.setText("ΕΚΚΙΝΗΣΗ FREELLMAPI ΣΤΟ TERMUX");
    root.addView(startButton);

    Button open = new Button(this);
    open.setText("ΑΝΟΙΓΜΑ DASHBOARD");
    root.addView(open);

    browser = new WebView(this);
    browser.getSettings().setJavaScriptEnabled(true);
    browser.getSettings().setDomStorageEnabled(true);
    browser.setWebViewClient(new WebViewClient() {
      @Override public void onReceivedError(WebView view, WebResourceRequest request, android.webkit.WebResourceError error) {
        if (request.isForMainFrame()) info.setText("Ο server δεν λειτουργεί ακόμη. Πάτησε Εκκίνηση και άφησε το Termux ανοιχτό.");
      }
      @Override public void onPageFinished(WebView view, String url) {
        if (url.startsWith(DASHBOARD)) info.setText("Συνδέθηκε στο τοπικό FreeLLMAPI.");
      }
    });
    root.addView(browser, new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, 0, 1));

    startButton.setOnClickListener(v -> startInTermux());
    open.setOnClickListener(v -> browser.loadUrl(DASHBOARD));
    setContentView(root);
    browser.loadUrl(DASHBOARD);
  }

  private void startInTermux() {
    if (!isPackageInstalled(TERMUX)) {
      info.setText("Δεν βρέθηκε το Termux. Εγκατέστησέ το από το F-Droid και άνοιξέ το μία φορά.");
      try { startActivity(new Intent(Intent.ACTION_VIEW, Uri.parse("https://f-droid.org/packages/com.termux/"))); } catch (Exception ignored) {}
      return;
    }

    if (checkSelfPermission("com.termux.permission.RUN_COMMAND") != PackageManager.PERMISSION_GRANTED) {
      info.setText("Χρειάζεται να επιτρέψεις την άδεια «Run commands in Termux environment» στο επόμενο μήνυμα.");
      requestPermissions(new String[]{"com.termux.permission.RUN_COMMAND"}, REQUEST_TERMUX_PERMISSION);
      return;
    }
    launchTermuxCommand();
  }

  @Override public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] grantResults) {
    super.onRequestPermissionsResult(requestCode, permissions, grantResults);
    if (requestCode == REQUEST_TERMUX_PERMISSION) {
      if (grantResults.length > 0 && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
        info.setText("Η άδεια δόθηκε. Ξεκινά το FreeLLMAPI…");
        launchTermuxCommand();
      } else {
        info.setText("Η άδεια δεν δόθηκε. Άνοιξε Ρυθμίσεις Android → Εφαρμογές → FreeLLMAPI → Δικαιώματα → Πρόσθετα δικαιώματα → Run commands in Termux environment και επίτρεψέ την.");
        try {
          Intent settings = new Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS, Uri.parse("package:" + getPackageName()));
          startActivity(settings);
        } catch (Exception ignored) {}
      }
    }
  }

  private void launchTermuxCommand() {
    String script =
      "set -e; " +
      "if ! command -v node >/dev/null 2>&1 || ! command -v git >/dev/null 2>&1; then pkg update -y && pkg install -y nodejs-lts git; fi; " +
      "if [ ! -d \"$HOME/freellmapi/.git\" ]; then git clone https://github.com/tashfeenahmed/freellmapi.git \"$HOME/freellmapi\"; fi; " +
      "cd \"$HOME/freellmapi\"; " +
      "if [ ! -x node_modules/.bin/concurrently ]; then npm install --no-audit --no-fund; fi; " +
      "npm run dev";
    try {
      Intent intent = new Intent("com.termux.RUN_COMMAND");
      intent.setClassName(TERMUX, "com.termux.app.RunCommandService");
      intent.putExtra("com.termux.RUN_COMMAND_PATH", "/data/data/com.termux/files/usr/bin/bash");
      intent.putExtra("com.termux.RUN_COMMAND_ARGUMENTS", new String[]{"-lc", script});
      intent.putExtra("com.termux.RUN_COMMAND_WORKDIR", "/data/data/com.termux/files/home");
      intent.putExtra("com.termux.RUN_COMMAND_BACKGROUND", false);
      startService(intent);
      info.setText("Εστάλη η εκκίνηση στο Termux. Αν είναι η πρώτη φορά, περίμενε να εγκατασταθούν Node.js και FreeLLMAPI. Άφησε το Termux ανοιχτό.");
    } catch (Exception e) {
      info.setText("Δεν ξεκίνησε το Termux: " + e.getMessage());
    }
  }

  private boolean isPackageInstalled(String packageName) {
    try { getPackageManager().getPackageInfo(packageName, 0); return true; }
    catch (PackageManager.NameNotFoundException e) { return false; }
  }

  @Override public void onBackPressed() {
    if (browser != null && browser.canGoBack()) browser.goBack();
    else super.onBackPressed();
  }
}
