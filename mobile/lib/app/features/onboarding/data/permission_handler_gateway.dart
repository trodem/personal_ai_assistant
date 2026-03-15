import 'package:permission_handler/permission_handler.dart';

import '../domain/device_permissions_gateway.dart';

class PermissionHandlerGateway implements DevicePermissionsGateway {
  @override
  Future<bool> request(AppPermission permission) async {
    final PermissionStatus status = await _map(permission).request();
    return status.isGranted;
  }

  @override
  Future<bool> openSettings() async {
    return openAppSettings();
  }

  Permission _map(AppPermission permission) {
    switch (permission) {
      case AppPermission.microphone:
        return Permission.microphone;
      case AppPermission.camera:
        return Permission.camera;
    }
  }
}
