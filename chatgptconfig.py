for app in base_dir_apps:
        allowed_apps = []

        if Employee.objects.filter(is_pms=True).exists():
            allowed_apps.append('pms')

        if Employee.objects.filter(leave_active=True).exists():
            allowed_apps.append('leave')

        if Employee.objects.filter(assets_active=True).exists():
            allowed_apps.append('asset')

        if Employee.objects.filter(payroll_active=True).exists():
            allowed_apps.append('payroll')

        if Employee.objects.filter(attendance_active=True).exists():
            allowed_apps.append('attendance')

        # Default allowed apps if none of the above conditions match
        if not allowed_apps:
            allowed_apps = ['attendance', 'payroll', 'leave', 'recruitment', 'employee', 'offboarding', 'pms', 'helpdesk', 'asset', 'onboarding']

        if app not in allowed_apps:
            continue  # Skip apps that are not allowed

        try:
            sidebar_module = importlib.import_module(app + ".sidebar")
        except Exception as e:
            logger.error(f"Failed to import sidebar for {app}: {e}")
            continue

        if sidebar_module:
            accessibility = None
            if getattr(sidebar_module, "ACCESSIBILITY", None):
                accessibility = import_method(sidebar_module.ACCESSIBILITY)

            # Check if the user has access to view this menu
            if not accessibility or accessibility(
                    request,
                    sidebar_module.MENU,
                    PermWrapper(request.user),
            ):
                MENU = {
                    "menu": sidebar_module.MENU,
                    "app": app,
                    "img_src": getattr(sidebar_module, "IMG_SRC", None),
                    "submenu": [],
                }
                MENUS.append(MENU)

                # Process submenus
                for submenu in getattr(sidebar_module, "SUBMENUS", []):
                    submenu_accessibility = None
                    if submenu.get("accessibility"):
                        submenu_accessibility = import_method(submenu["accessibility"])

                    # Check if the user has access to view this submenu
                    if not submenu_accessibility or submenu_accessibility(
                            request,
                            submenu,
                            PermWrapper(request.user),
                    ):
                        # Process submenu item (e.g., modify redirect URL)
                        redirect = submenu.get("redirect", "").split("?")[0]
                        submenu["redirect"] = redirect
                        MENU["submenu"].append(submenu)

    ALL_MENUS[request.session.session_key] = MENUS
