"""
horilla/config.py

Horilla app configurations
"""
# horilla/config.py

import importlib
import logging
from django.contrib.auth.context_processors import PermWrapper
from employee.models import Employee
from horilla.horilla_apps import SIDEBARS

logger = logging.getLogger(__name__)

def import_method(accessibility):
    module_path, method_name = accessibility.rsplit(".", 1)
    module = __import__(module_path, fromlist=[method_name])
    accessibility_method = getattr(module, method_name)
    return accessibility_method

ALL_MENUS = {}

def sidebar(request):
    base_dir_apps = SIDEBARS
    # allowed_apps = ['attendance', 'payroll', 'leave','recruitment','employee','offboarding','helpdesk','asset','pms','onboarding']  # Define which apps are allowed to load their sidebar
    
    if not request.user.is_anonymous:
        request.MENUS = []
        MENUS = request.MENUS

        for app in base_dir_apps:
            if Employee.objects.filter(is_pms = True):
                
                if Employee.objects.filter(leave_active = True):
                    
                    if Employee.objects.filter(assets_active = True):

                        if Employee.objects.filter(payroll_active = True):

                            if Employee.objects.filter(attendance_active = True):
                                allowed_apps = ['pms','leave','asset','payroll','attendance']
                            else:
                                allowed_apps = ['pms','leave','asset','payroll']      
                        else:
                            allowed_apps = ['pms','leave','asset'] 
                    else:
                        allowed_apps = ['pms','leave']                 
                else:
                    allowed_apps = ['pms']            
            allowed_apps = ['attendance', 'payroll', 'leave','recruitment','employee','offboarding','pms','helpdesk','asset','onboarding']

                        


            if app not in allowed_apps:
                continue  # Skip apps that are not allowed

            try:
                sidebar = importlib.import_module(app + ".sidebar")
            except Exception as e:
                logger.error(f"Failed to import sidebar for {app}: {e}")
                continue

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

        ALL_MENUS[request.session.session_key] = MENUS

def get_MENUS(request):
    ALL_MENUS[request.session.session_key] = []
    sidebar(request)
    return {"sidebar": ALL_MENUS.get(request.session.session_key)}
