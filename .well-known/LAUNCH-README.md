# Deep-link association files — fill in at App Store / Play Store launch

These two files make `https://billtracking.org/p/...` links open the **app**
(iOS Universal Links / Android App Links) instead of the browser. They are
**scaffolded with placeholders** and are NOT launch-ready yet — the values below
only exist once the app is registered with Apple and Google.

GitHub Pages serves this folder because the site has a `.nojekyll` file (Jekyll
would otherwise hide dot-folders). No build step needed — just commit and push.

## `apple-app-site-association` (iOS)
- No file extension (correct — do not add `.json`).
- Replace `REPLACE_TEAM_ID` with your **Apple Developer Team ID** (App Store
  Connect → Membership).
- Replace `REPLACE_IOS_BUNDLE_ID` with the app's **bundle identifier** (must
  match `ios.bundleIdentifier` in `app/app.json`).
- Result looks like: `"appID": "A1B2C3D4E5.org.billtracking.app"`.

## `assetlinks.json` (Android)
- Replace `REPLACE_ANDROID_PACKAGE` with the app's **package name** (must match
  `android.package` in `app/app.json`).
- Replace `REPLACE_SHA256_FINGERPRINT` with the **SHA-256 fingerprint of the
  signing key** used to publish the app (from Play Console → App integrity, or
  `keytool -list -v -keystore <your.keystore>`). Multiple fingerprints allowed.

## The app side is already wired
- `app/app.json`: `ios.associatedDomains` = `applinks:billtracking.org`,
  `android.intentFilters` for `https://billtracking.org/p/*`, `scheme` =
  `billtracking`.
- `app/src/app/p/[id].tsx`: resolves an incoming `/p/<id>` to its post and lands
  the user on it in the Home feed.

## Verify after filling + deploying
1. `https://billtracking.org/.well-known/apple-app-site-association` returns the
   JSON (ideally served as `application/json`; modern iOS is tolerant).
2. `https://billtracking.org/.well-known/assetlinks.json` returns the JSON.
3. On a device with the installed (store or TestFlight/internal) build, tapping a
   `billtracking.org/p/...` link opens the app on that post.
4. Apple's validator: https://search.developer.apple.com/appsearch-validation-tool/
