

import importlib
import logging
from django.contrib.auth.context_processors import PermWrapper
from employee.models import Employee
from horilla.horilla_apps import SIDEBARS

logger = logging.getLogger(__name__)

ALL_MENUS = {}  # Define ALL_MENUS at the module level

def import_method(accessibility):
    module_path, method_name = accessibility.rsplit(".", 1)
    module = __import__(module_path, fromlist=[method_name])
    accessibility_method = getattr(module, method_name)
    return accessibility_method

def process_sidebar(app, request, MENUS):
    try:
        sidebar = importlib.import_module(app + ".sidebar")
    except Exception as e:
        logger.error(f"Failed to import sidebar for {app}: {e}")
        return

    if sidebar:
        accessibility = None
        if getattr(sidebar, "ACCESSIBILITY", None):
            accessibility = import_method(sidebar.ACCESSIBILITY)

        # Check if the user has access to view this menu
        if not accessibility or accessibility(
            request,
            sidebar.MENU,
            PermWrapper(request.user),
        ):
            MENU = {
                "menu": sidebar.MENU,
                "app": app,
                "img_src": sidebar.IMG_SRC,
                "submenu": [],
            }
            MENUS.append(MENU)

            # Process submenus
            for submenu in sidebar.SUBMENUS:
                accessibility = None
                if submenu.get("accessibility"):
                    accessibility = import_method(submenu["accessibility"])

                # Check if the user has access to view this submenu
                if not accessibility or accessibility(
                    request,
                    submenu,
                    PermWrapper(request.user),
                ):
                    # Process submenu item (e.g., modify redirect URL)
                    redirect = submenu["redirect"].split("?")[0]
                    submenu["redirect"] = redirect
                    MENU["submenu"].append(submenu)

def sidebar(request):
    base_dir_apps = SIDEBARS
    allowed_apps = ['attendance', 'payroll', 'leave', 'recruitment', 'employee', 'offboarding', 'helpdesk', 'asset', 'pms', 'onboarding']

    if not request.user.is_anonymous:
        request.MENUS = []
        MENUS = request.MENUS

        for app in base_dir_apps:
            if app in allowed_apps:
                if app == 'pms' and request.user.employee_get.is_pms:
                    process_sidebar(app, request, MENUS)

                elif app == 'leave' and request.user.employee_get.leave_active:
                    process_sidebar(app, request, MENUS)

                elif app == 'payroll' and request.user.employee_get.payroll_active:
                    process_sidebar(app, request, MENUS)

                elif app == 'attendance' and request.user.employee_get.attendance_active:
                    process_sidebar(app, request, MENUS)

                elif app == 'asset' and request.user.employee_get.assets_active:
                    process_sidebar(app, request, MENUS)

                elif app == 'employee' and request.user.employee_get.employee_active:
                    process_sidebar(app, request, MENUS)    

                elif app == 'recruitment' and request.user.employee_get.admin_pms:
                    process_sidebar(app, request, MENUS)

                elif app == 'onboarding' and request.user.employee_get.admin_pms:
                    process_sidebar(app, request, MENUS)

                elif app == 'offboarding' and request.user.employee_get.admin_pms:
                    process_sidebar(app, request, MENUS)            

        ALL_MENUS[request.session.session_key] = MENUS  # Store MENUS in ALL_MENUS

def get_MENUS(request):
    ALL_MENUS[request.session.session_key] = []  # Initialize ALL_MENUS for the session key
    sidebar(request)
    return {"sidebar": ALL_MENUS.get(request.session.session_key)}  # Return the sidebar for the session key
