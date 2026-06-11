import 'package:local_auth/local_auth.dart';

/// Wraps [LocalAuthentication] so the rest of the app never imports
/// `local_auth` directly.
///
/// Compatible with local_auth **3.0.1** — the 3.x API removed
/// [AuthenticationOptions] and [stickyAuth]; options are now named
/// parameters on [authenticate] directly, and the exception type changed
/// from [PlatformException] to [LocalAuthException].
///
/// Registered as a singleton in GetIt.
class BiometricService {
  BiometricService() : _auth = LocalAuthentication();

  final LocalAuthentication _auth;

  // ── Availability ───────────────────────────────────────────────────────────

  /// Returns true if the device supports biometrics AND the user has at
  /// least one biometric enrolled (fingerprint or face ID).
  ///
  /// This is the single gate used to decide whether to show the biometric
  /// button on the login screen. Both checks are required:
  ///   - [canCheckBiometrics]    → hardware present
  ///   - [getAvailableBiometrics] → something actually enrolled
  ///
  /// A device can report hardware as available but have zero biometrics
  /// enrolled (e.g. a fresh Android phone before any fingerprint is set up).
  Future<bool> isAvailable() async {
    try {
      final canCheck = await _auth.canCheckBiometrics;
      if (!canCheck) return false;

      final enrolled = await _auth.getAvailableBiometrics();
      return enrolled.isNotEmpty;
    } on LocalAuthException {
      return false;
    }
  }

  /// Returns the primary biometric type enrolled on this device, or null.
  ///
  /// Used by the login screen to pick the correct icon:
  ///   - Face ID (iOS)              → [BiometricType.face]
  ///   - Fingerprint / Touch ID     → [BiometricType.fingerprint]
  ///   - Android strong biometric   → [BiometricType.strong]
  Future<BiometricType?> availableType() async {
    try {
      final enrolled = await _auth.getAvailableBiometrics();
      if (enrolled.isEmpty) return null;
      if (enrolled.contains(BiometricType.face)) return BiometricType.face;
      if (enrolled.contains(BiometricType.fingerprint)) {
        return BiometricType.fingerprint;
      }
      return enrolled.first;
    } on LocalAuthException {
      return null;
    }
  }

  // ── Authentication ─────────────────────────────────────────────────────────

  /// Triggers the OS biometric prompt and returns true on success.
  ///
  /// All [LocalAuthException]s are caught and mapped to false — callers
  /// never need exception handling. A failed biometric simply leaves the
  /// user on the login screen to use their password instead.
  ///
  /// [biometricOnly] is true by default — passcode/pin fallback is
  /// intentionally disabled. The password field is right there.
  ///
  /// [persistAcrossBackgrounding] replaces the old `stickyAuth` from 2.x.
  /// It keeps the auth dialog alive if the app is backgrounded mid-prompt.
  Future<bool> authenticate({
    String localizedReason = 'Sign in to Throve',
    bool biometricOnly = true,
  }) async {
    try {
      return await _auth.authenticate(
        localizedReason: localizedReason,
        biometricOnly: biometricOnly,
        persistAcrossBackgrounding: true,
      );
    } on LocalAuthException {
      return false;
    }
  }
}