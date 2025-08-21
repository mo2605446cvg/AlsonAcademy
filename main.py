import flet as ft
import requests
import json
from user import User
from content import Content
from message import Message
import webbrowser
import os
from datetime import datetime
from functools import partial
import threading
import time
import locale

# تعيين اللغة العربية
try:
    locale.setlocale(locale.LC_ALL, 'ar_AE.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_ALL, 'Arabic')
    except:
        pass

API_URL = "https://ki74.alalsunacademy.com/api"

def main(page: ft.Page):
    # إعدادات التصميم الحديث
    page.title = "أكاديمية الألسن"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_resizable = True
    page.window_min_width = 360
    page.window_min_height = 640
    page.padding = 0
    page.rtl = True  # تمكين الدعم الكامل للغة العربية
    page.fonts = {
        "Cairo": "https://fonts.googleapis.com/css2?family=Cairo&display=swap",
        "Cairo-Bold": "https://fonts.googleapis.com/css2?family=Cairo:wght@700&display=swap"
    }
    page.theme = ft.Theme(
        font_family="Cairo",
        color_scheme=ft.ColorScheme(
            primary="#128C7E",  # لون WhatsApp
            primary_container="#075E54",
            secondary="#25D366",
            surface="#FFFFFF",
            background="#F0F2F5",
            on_primary=ft.Colors.WHITE,
            on_surface=ft.Colors.BLACK,
        ),
        text_theme=ft.TextTheme(
            body_large=ft.TextStyle(font_family="Cairo", size=16),
            title_large=ft.TextStyle(font_family="Cairo-Bold", size=24, weight=ft.FontWeight.BOLD)
        )
    )
    
    page.dark_theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary="#128C7E",
            primary_container="#075E54",
            secondary="#25D366",
            surface="#1F2C34",
            background="#121B22",
            on_primary=ft.Colors.WHITE,
            on_surface=ft.Colors.WHITE,
        )
    )
    
    page.bgcolor = page.theme.color_scheme.background
    page.client_storage.clear()

    # إعدادات الشريط الجانبي
    nav_rail_visible = True
    page.user = None

    # مؤشر التحميل
    loading_indicator = ft.ProgressRing(visible=False, width=50, height=50, stroke_width=3)
    page.overlay.append(loading_indicator)

    # متغيرات التخزين المؤقت
    content_cache = {}
    messages_cache = {}

    # وظائف مساعدة
    def show_loading(visible):
        loading_indicator.visible = visible
        page.update()

    def show_error(message):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(message, text_align=ft.TextAlign.CENTER, color=ft.Colors.WHITE),
            bgcolor=ft.Colors.RED_700,
            duration=3000,
        )
        page.snack_bar.open = True
        page.update()

    def show_success(message):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(message, text_align=ft.TextAlign.CENTER, color=ft.Colors.WHITE),
            bgcolor=ft.Colors.GREEN_700,
            duration=3000,
        )
        page.snack_bar.open = True
        page.update()

    def toggle_theme(e):
        page.theme_mode = ft.ThemeMode.DARK if page.theme_mode == ft.ThemeMode.LIGHT else ft.ThemeMode.LIGHT
        page.bgcolor = page.theme.color_scheme.background
        page.update()

    def require_login(func):
        """ديكوراتور للتحقق من تسجيل الدخول"""
        def wrapper(*args, **kwargs):
            if not page.user:
                login_screen()
                return
            return func(*args, **kwargs)
        return wrapper

    def require_admin(func):
        """ديكوراتور للتحقق من صلاحيات المدير"""
        def wrapper(*args, **kwargs):
            if not page.user or page.user.role != "admin":
                show_error("غير مصرح لك بهذا الإجراء")
                return
            return func(*args, **kwargs)
        return wrapper

    # وظائف API
    def login_user(code, password):
        if not code or not password:
            show_error("يرجى إدخال كود المستخدم وكلمة المرور")
            return None
        
        show_loading(True)
        try:
            response = requests.post(
                f"{API_URL}/api.php?table=users&action=login",
                json={"code": code, "password": password},
                headers={"Content-Type": "application/json"},
                timeout=10,
            )
            if response.status_code == 200:
                try:
                    user_data = response.json()
                    page.client_storage.set("user", json.dumps(user_data))
                    page.user = User.from_json(user_data)
                    return page.user
                except json.JSONDecodeError:
                    show_error("خطأ في استجابة السيرفر: تنسيق غير صالح")
                    return None
            else:
                try:
                    error_message = response.json().get("error", "خطأ غير معروف")
                except:
                    error_message = "خطأ في استجابة السيرفر"
                show_error(error_message)
                return None
        except Exception as e:
            show_error("فشل في الاتصال بالسيرفر: تأكد من الإنترنت")
            return None
        finally:
            show_loading(False)

    def get_content(department, division):
        cache_key = f"{department}-{division}"
        if cache_key in content_cache:
            return content_cache[cache_key]
        
        show_loading(True)
        try:
            url = f"{API_URL}/api.php?table=content"
            if department and division:
                url += f"&department={department}&division={division}"
            response = requests.get(url, headers={"Content-Type": "application/json"}, timeout=10)
            if response.status_code == 200:
                content_list = [Content.from_json(item) for item in response.json()]
                content_cache[cache_key] = content_list
                return content_list
            else:
                show_error("فشل في جلب المحتوى")
                return []
        except Exception as e:
            show_error("فشل في الاتصال بالسيرفر")
            return []
        finally:
            show_loading(False)

    @require_admin
    def upload_content(title, file_path, uploaded_by, department, division, description):
        show_loading(True)
        try:
            with open(file_path, "rb") as file:
                files = {"file": (os.path.basename(file_path), file, "application/octet-stream")}
                data = {
                    "title": title,
                    "uploaded_by": uploaded_by,
                    "department": department,
                    "division": division,
                    "description": description,
                }
                response = requests.post(
                    f"{API_URL}/upload.php",
                    data=data,
                    files=files,
                    timeout=30,  # زيادة المهلة للرفع
                )
                if response.status_code == 200:
                    show_success("تم رفع المحتوى بنجاح")
                    # مسح المحتوى المخزن مؤقتاً
                    cache_key = f"{department}-{division}"
                    if cache_key in content_cache:
                        del content_cache[cache_key]
                    return True
                else:
                    show_error(f"فشل في رفع المحتوى: {response.text}")
                    return False
        except Exception as e:
            show_error(f"فشل في رفع المحتوى: {e}")
            return False
        finally:
            show_loading(False)

    @require_admin
    def delete_content(id, department, division):
        show_loading(True)
        try:
            response = requests.delete(
                f"{API_URL}/api.php?table=content",
                json={"id": id},
                headers={"Content-Type": "application/json"},
                timeout=10,
            )
            if response.status_code == 200:
                show_success("تم حذف المحتوى بنجاح")
                # مسح المحتوى المخزن مؤقتاً
                cache_key = f"{department}-{division}"
                if cache_key in content_cache:
                    del content_cache[cache_key]
                return True
            else:
                show_error(f"فشل في حذف المحتوى: {response.text}")
                return False
        except Exception as e:
            show_error("فشل في الاتصال بالسيرفر")
            return False
        finally:
            show_loading(False)

    def get_chat_messages(department, division):
        cache_key = f"{department}-{division}"
        if cache_key in messages_cache:
            return messages_cache[cache_key]
        
        try:
            url = f"{API_URL}/api.php?table=messages"
            if department and division:
                url += f"&department={department}&division={division}"
            response = requests.get(url, headers={"Content-Type": "application/json"}, timeout=10)
            if response.status_code == 200:
                messages = [Message.from_json(item) for item in response.json()]
                messages_cache[cache_key] = messages
                return messages
            else:
                show_error("فشل في جلب الرسائل")
                return []
        except Exception as e:
            show_error("فشل في الاتصال بالسيرفر")
            return []

    def send_message(sender_id, department, division, content):
        try:
            id = str(int(datetime.now().timestamp() * 1000))
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            response = requests.post(
                f"{API_URL}/api.php?table=messages",
                json={
                    "id": id,
                    "content": content,
                    "sender_id": sender_id,
                    "department": department,
                    "division": division,
                    "timestamp": timestamp,
                },
                headers={"Content-Type": "application/json"},
                timeout=10,
            )
            if response.status_code == 200:
                # مسح الرسائل المخزنة مؤقتاً
                cache_key = f"{department}-{division}"
                if cache_key in messages_cache:
                    del messages_cache[cache_key]
                return True
            else:
                show_error(f"فشل في إرسال الرسالة: {response.text}")
                return False
        except Exception as e:
            show_error("فشل في إرسال الرسالة")
            return False

    @require_admin
    def get_users():
        try:
            response = requests.get(
                f"{API_URL}/api.php?table=users&action=all",
                headers={"Content-Type": "application/json"},
                timeout=10,
            )
            if response.status_code == 200:
                return [User.from_json(item) for item in response.json()]
            else:
                show_error("فشل في جلب المستخدمين")
                return []
        except Exception as e:
            show_error("فشل في الاتصال بالسيرفر")
            return []

    @require_admin
    def add_user(code, username, department, division, role, password):
        show_loading(True)
        try:
            response = requests.post(
                f"{API_URL}/api.php?table=users&action=add",
                json={
                    "code": code,
                    "username": username,
                    "department": department,
                    "division": division,
                    "role": role,
                    "password": password,
                },
                headers={"Content-Type": "application/json"},
                timeout=10,
            )
            if response.status_code == 200:
                show_success("تم إضافة المستخدم بنجاح")
                return True
            else:
                show_error(f"فشل في إضافة المستخدم: {response.text}")
                return False
        except Exception as e:
            show_error("فشل في إضافة المستخدم")
            return False
        finally:
            show_loading(False)

    @require_admin
    def delete_user(code):
        show_loading(True)
        try:
            response = requests.delete(
                f"{API_URL}/api.php?table=users",
                json={"code": code},
                headers={"Content-Type": "application/json"},
                timeout=10,
            )
            if response.status_code == 200:
                show_success("تم حذف المستخدم بنجاح")
                return True
            else:
                show_error(f"فشل في حذف المستخدم: {response.text}")
                return False
        except Exception as e:
            show_error("فشل في حذف المستخدم")
            return False
        finally:
            show_loading(False)

    # مكونات الواجهة
    def get_navigation_rail(user):
        destinations = [
            ft.NavigationRailDestination(
                icon=ft.Icons.HOME_OUTLINED,
                selected_icon=ft.Icons.HOME,
                label="الرئيسية",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.LIST_OUTLINED,
                selected_icon=ft.Icons.LIST,
                label="المحتوى",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.CHAT_BUBBLE_OUTLINED,
                selected_icon=ft.Icons.CHAT_BUBBLE,
                label="الشات",
            ),
        ]
        if user.role == "admin":
            destinations.extend([
                ft.NavigationRailDestination(
                    icon=ft.Icons.UPLOAD_OUTLINED,
                    selected_icon=ft.Icons.UPLOAD,
                    label="رفع",
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.PEOPLE_OUTLINED,
                    selected_icon=ft.Icons.PEOPLE,
                    label="المستخدمين",
                ),
            ])
        destinations.append(
            ft.NavigationRailDestination(
                icon=ft.Icons.LOGOUT_OUTLINED,
                selected_icon=ft.Icons.LOGOUT,
                label="تسجيل الخروج",
            )
        )

        def on_nav_change(e):
            index = e.control.selected_index
            try:
                if index == 0:
                    show_home()
                elif index == 1:
                    show_content_list()
                elif index == 2:
                    show_chat()
                elif user.role == "admin" and index == 3:
                    show_content_upload()
                elif user.role == "admin" and index == 4:
                    show_user_management()
                elif (user.role == "admin" and index == 5) or (user.role != "admin" and index == 3):
                    logout()
            except Exception as e:
                show_error(f"خطأ في التنقل: {e}")

        nav_rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=100,
            bgcolor=page.theme.color_scheme.primary_container,
            indicator_color=page.theme.color_scheme.primary,
            destinations=destinations,
            on_change=on_nav_change,
            elevation=1,
            group_alignment=0.0,
            extended=True,
            expand=True,
        )

        nav_rail_container = ft.Container(
            content=nav_rail,
            width=250,
            height=page.height,
            bgcolor=page.theme.color_scheme.primary_container,
            padding=ft.padding.symmetric(vertical=20, horizontal=10),
            visible=nav_rail_visible,
            animate=ft.Animation(300, ft.AnimationCurve.EASE_IN_OUT),
        )

        def toggle_nav_rail(e):
            nonlocal nav_rail_visible
            nav_rail_visible = not nav_rail_visible
            nav_rail_container.visible = nav_rail_visible
            toggle_button.icon = ft.Icons.MENU if nav_rail_visible else ft.Icons.MENU_OPEN
            page.update()

        toggle_button = ft.IconButton(
            icon=ft.Icons.MENU,
            icon_color=ft.Colors.WHITE,
            bgcolor=page.theme.color_scheme.primary,
            on_click=toggle_nav_rail,
            tooltip="إظهار/إخفاء القائمة",
            top=10,
            right=10,
            style=ft.ButtonStyle(shape=ft.CircleBorder(), padding=15)
        )

        return ft.Stack(
            [
                nav_rail_container,
                toggle_button
            ]
        )

    def logout():
        page.user = None
        page.client_storage.clear()
        login_screen()

    def login_screen():
        code_field = ft.TextField(
            label="كود المستخدم",
            prefix_icon=ft.Icons.PERSON,
            border_radius=15,
            filled=True,
            text_align=ft.TextAlign.RIGHT,
            width=300
        )
        password_field = ft.TextField(
            label="كلمة المرور",
            prefix_icon=ft.Icons.LOCK,
            password=True,
            can_reveal_password=True,
            border_radius=15,
            filled=True,
            text_align=ft.TextAlign.RIGHT,
            width=300
        )

        def on_login(e):
            user = login_user(code_field.value, password_field.value)
            if user:
                show_home()

        login_card = ft.Card(
            elevation=8,
            content=ft.Container(
                width=400,
                padding=30,
                content=ft.Column(
                    [
                        ft.Image(
                            src="https://via.placeholder.com/150?text=Alson+Logo",
                            width=120,
                            height=120,
                            fit=ft.ImageFit.CONTAIN
                        ),
                        ft.Text("أكاديمية الألسن", 
                                size=28, 
                                weight=ft.FontWeight.BOLD, 
                                color=page.theme.color_scheme.primary),
                        ft.Divider(height=30),
                        code_field,
                        password_field,
                        ft.ElevatedButton(
                            "تسجيل الدخول",
                            icon=ft.Icons.LOGIN,
                            on_click=on_login,
                            style=ft.ButtonStyle(
                                padding=20,
                                shape=ft.RoundedRectangleBorder(radius=15),
                            ),
                            color=ft.Colors.WHITE,
                            bgcolor=page.theme.color_scheme.primary,
                            width=300
                        ),
                        ft.TextButton("نسيت كلمة المرور؟")
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=20
                )
            )
        )

        page.controls.clear()
        page.add(
            ft.Container(
                content=ft.Column(
                    [
                        ft.Row([login_card], alignment=ft.MainAxisAlignment.CENTER)
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    expand=True
                ),
                gradient=ft.LinearGradient(
                    begin=ft.alignment.top_left,
                    end=ft.alignment.bottom_right,
                    colors=[page.theme.color_scheme.primary_container, 
                            page.theme.color_scheme.background]
                )
            )
        )
        page.update()

    @require_login
    def show_content_list():
        content = get_content(page.user.department, page.user.division)

        def refresh_content(e):
            nonlocal content
            content = get_content(page.user.department, page.user.division)
            content_list.controls = build_content_list()
            page.update()

        def get_file_icon(file_type):
            if file_type == "pdf":
                return ft.Icons.PICTURE_AS_PDF
            elif file_type in ["jpg", "png", "jpeg"]:
                return ft.Icons.IMAGE
            elif file_type == "txt":
                return ft.Icons.TEXT_SNIPPET
            else:
                return ft.Icons.INSERT_DRIVE_FILE

        def build_content_list():
            controls = []
            for item in content:
                def on_view(e, item=item):
                    url = f"https://ki74.alalsunacademy.com/{item.file_path}"
                    if item.file_type == "pdf":
                        webbrowser.open(url)
                    elif item.file_type in ["jpg", "png", "jpeg"]:
                        show_image_viewer(url)
                    elif item.file_type == "txt":
                        show_text_viewer(url)

                def on_delete(e, item=item):
                    def confirm_delete(e):
                        if delete_content(item.id, page.user.department, page.user.division):
                            refresh_content(None)
                        page.dialog.open = False
                        page.update()

                    page.dialog = ft.AlertDialog(
                        title=ft.Text("تأكيد الحذف", text_align=ft.TextAlign.CENTER),
                        content=ft.Text("هل أنت متأكد من حذف هذا المحتوى؟", text_align=ft.TextAlign.CENTER),
                        actions=[
                            ft.TextButton("إلغاء", on_click=lambda e: setattr(page.dialog, "open", False)),
                            ft.TextButton("حذف", on_click=confirm_delete, style=ft.ButtonStyle(color=ft.Colors.RED)),
                        ],
                        actions_alignment=ft.MainAxisAlignment.CENTER,
                    )
                    page.dialog.open = True
                    page.update()

                actions = [
                    ft.IconButton(ft.Icons.VISIBILITY, on_click=on_view, tooltip="عرض"),
                ]
                if page.user.role == "admin":
                    actions.append(ft.IconButton(ft.Icons.DELETE, icon_color=ft.Colors.RED, on_click=on_delete, tooltip="حذف"))

                controls.append(
                    ft.Card(
                        content=ft.Container(
                            content=ft.ResponsiveRow(
                                [
                                    ft.Column(
                                        col={"sm": 2, "md": 1},
                                        controls=[
                                            ft.IconButton(
                                                icon=get_file_icon(item.file_type),
                                                icon_size=40,
                                                icon_color=page.theme.color_scheme.primary,
                                                tooltip=item.file_type.upper(),
                                                on_click=on_view
                                            )
                                        ],
                                        alignment=ft.MainAxisAlignment.CENTER,
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    ),
                                    ft.Column(
                                        col={"sm": 7, "md": 9},
                                        controls=[
                                            ft.Text(item.title, weight=ft.FontWeight.BOLD, size=16),
                                            ft.Text(f"نوع الملف: {item.file_type}", size=14, color=ft.Colors.SECONDARY),
                                            ft.Text(f"حجم الملف: {item.formatted_size}", size=14, color=ft.Colors.SECONDARY),
                                            ft.Text(f"تم الرفع بواسطة: {item.uploaded_by}", size=14, color=ft.Colors.SECONDARY),
                                            ft.Text(f"تاريخ الرفع: {item.upload_date}", size=14, color=ft.Colors.SECONDARY),
                                            ft.Text(f"نبذة: {item.description}", size=14, max_lines=2, overflow=ft.TextOverflow.ELLIPSIS),
                                        ],
                                        alignment=ft.MainAxisAlignment.CENTER,
                                        expand=True,
                                    ),
                                    ft.Column(
                                        col={"sm": 3, "md": 2},
                                        controls=actions,
                                        alignment=ft.MainAxisAlignment.CENTER,
                                        horizontal_alignment=ft.CrossAxisAlignment.END,
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                            padding=16,
                        ),
                        elevation=3,
                    )
                )
            return controls

        content_list = ft.ListView(controls=build_content_list(), expand=True, spacing=10, padding=10)

        search_field = ft.TextField(
            label="بحث في المحتوى...",
            on_change=lambda e: filter_content(),
            width=300,
            rtl=True,
            border_radius=10,
        )

        def filter_content():
            if not search_field.value:
                content_list.controls = build_content_list()
            else:
                filtered = [item for item in content if search_field.value.lower() in item.title.lower()]
                content_list.controls = [
                    c for c in build_content_list() if any(item.title == c.content.content.controls[0].content.controls[1].controls[0].value for item in filtered)
                ]
            page.update()

        main_content = ft.Container(
            content=ft.Column(
                [
                    ft.Text("المحتوى", size=24, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                    ft.ResponsiveRow(
                        [
                            ft.Container(
                                col={"sm": 12, "md": 6},
                                content=search_field,
                            ),
                            ft.Container(
                                col={"sm": 12, "md": 6},
                                content=ft.ElevatedButton(
                                    "تحديث المحتوى",
                                    on_click=refresh_content,
                                    style=ft.ButtonStyle(padding=15),
                                    expand=True,
                                ),
                                padding=5,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    content_list,
                ],
                alignment=ft.MainAxisAlignment.START,
                spacing=15,
            ),
            padding=10,
            expand=True,
        )

        page.controls.clear()
        page.add(
            ft.Row(
                [
                    main_content,
                    get_navigation_rail(page.user),
                ],
                alignment=ft.MainAxisAlignment.END,
                expand=True,
            )
        )
        page.update()

    @require_login
    @require_admin
    def show_content_upload():
        title_field = ft.TextField(
            label="عنوان المحتوى",
            text_align=ft.TextAlign.CENTER,
            text_style=ft.TextStyle(font_family="Cairo", size=16),
            border_radius=10,
            width=300,
            rtl=True,
        )
        description_field = ft.TextField(
            label="نبذة عن المحتوى",
            text_align=ft.TextAlign.CENTER,
            text_style=ft.TextStyle(font_family="Cairo", size=16),
            border_radius=10,
            width=300,
            rtl=True,
            multiline=True,
            min_lines=3,
            max_lines=5,
        )
        file_name = ft.Text("لم يتم اختيار ملف", text_align=ft.TextAlign.CENTER)
        file_path = [None]

        def pick_file(e):
            file_picker = ft.FilePicker(
                on_result=lambda result: on_file_picked(result, file_name, file_path)
            )
            page.overlay.append(file_picker)
            page.update()
            file_picker.pick_files(
                allowed_extensions=["pdf", "jpg", "png", "jpeg", "txt"],
                allow_multiple=False
            )

        def on_file_picked(result, file_name, file_path):
            if result.files:
                file_name.value = f"الملف المختار: {result.files[0].name}"
                file_path[0] = result.files[0].path
                page.update()

        def upload(e):
            if not title_field.value or not file_path[0] or not description_field.value:
                show_error("يرجى إدخال العنوان، النبذة، واختيار ملف")
                return
            if upload_content(title_field.value, file_path[0], page.user.code, page.user.department, page.user.division, description_field.value):
                title_field.value = ""
                description_field.value = ""
                file_name.value = "لم يتم اختيار ملف"
                file_path[0] = None
                show_content_list()

        main_content = ft.Container(
            content=ft.Column(
                [
                    ft.Text("رفع محتوى", size=24, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                    ft.Container(
                        content=ft.Column(
                            [
                                title_field,
                                ft.Container(height=16),
                                description_field,
                                ft.Container(height=16),
                                ft.ElevatedButton(
                                    "اختيار ملف",
                                    on_click=pick_file,
                                    style=ft.ButtonStyle(padding=15),
                                ),
                                file_name,
                                ft.Container(height=16),
                                ft.ElevatedButton(
                                    "رفع المحتوى",
                                    on_click=upload,
                                    style=ft.ButtonStyle(padding=15),
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                        padding=16,
                        bgcolor=page.theme.color_scheme.surface,
                        border_radius=12,
                        shadow=ft.BoxShadow(blur_radius=5, color=ft.Colors.BLACK12),
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=20,
            ),
            padding=20,
            expand=True,
        )

        page.controls.clear()
        page.add(
            ft.Row(
                [
                    main_content,
                    get_navigation_rail(page.user),
                ],
                alignment=ft.MainAxisAlignment.END,
                expand=True,
            )
        )
        page.update()

    @require_login
    def show_chat():
        messages = get_chat_messages(page.user.department, page.user.division)

        def refresh_messages(e=None):
            nonlocal messages
            messages = get_chat_messages(page.user.department, page.user.division)
            chat_list.controls = build_chat_list()
            page.update()

        def send(e):
            if not message_field.value:
                show_error("يرجى إدخال رسالة")
                return
            if send_message(page.user.code, page.user.department, page.user.division, message_field.value):
                message_field.value = ""
                refresh_messages()

        def build_chat_list():
            controls = []
            for message in messages:
                is_me = message.sender_id == page.user.code
                controls.append(
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text(
                                    message.username,
                                    weight=ft.FontWeight.BOLD,
                                    size=14,
                                ),
                                ft.Text(
                                    message.content,
                                    size=16,
                                    max_lines=10,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                ),
                                ft.Text(
                                    message.timestamp,
                                    size=12,
                                    color=ft.Colors.SECONDARY,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.START,
                            spacing=5,
                        ),
                        padding=ft.padding.all(12),
                        margin=ft.margin.only(
                            left=100 if not is_me else 20, 
                            right=20 if not is_me else 100, 
                            top=4, 
                            bottom=4
                        ),
                        bgcolor=page.theme.color_scheme.primary_container if is_me else page.theme.color_scheme.surface,
                        border_radius=15,
                        alignment=ft.alignment.center_right if is_me else ft.alignment.center_left,
                        shadow=ft.BoxShadow(blur_radius=3, color=ft.Colors.BLACK12),
                    )
                )
            return controls

        chat_list = ft.ListView(
            controls=build_chat_list(), 
            expand=True, 
            spacing=10, 
            padding=10,
            auto_scroll=True
        )

        # تحديث الرسائل تلقائياً كل 10 ثواني
        def auto_refresh():
            while True:
                time.sleep(10)
                refresh_messages()

        threading.Thread(target=auto_refresh, daemon=True).start()

        message_field = ft.TextField(
            label="اكتب رسالتك...",
            text_align=ft.TextAlign.RIGHT,
            multiline=True,
            min_lines=1,
            max_lines=5,
            border_radius=30,
            expand=True,
            rtl=True,
        )

        main_content = ft.Container(
            content=ft.Column(
                [
                    ft.Text("الشات", size=24, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                    ft.ElevatedButton(
                        "تحديث الرسائل",
                        on_click=refresh_messages,
                        style=ft.ButtonStyle(padding=15),
                    ),
                    chat_list,
                    ft.Row(
                        [
                            message_field,
                            ft.IconButton(
                                ft.Icons.SEND,
                                on_click=send,
                                tooltip="إرسال",
                                style=ft.ButtonStyle(shape=ft.CircleBorder(), padding=10),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=10,
                    ),
                ],
                alignment=ft.MainAxisAlignment.START,
                spacing=15,
            ),
            padding=10,
            expand=True,
        )

        page.controls.clear()
        page.add(
            ft.Row(
                [
                    main_content,
                    get_navigation_rail(page.user),
                ],
                alignment=ft.MainAxisAlignment.END,
                expand=True,
            )
        )
        page.update()

    @require_login
    @require_admin
    def show_user_management():
        users = get_users()

        def refresh_users(e):
            nonlocal users
            users = get_users()
            user_list.controls = build_user_list()
            page.update()

        def build_user_list():
            controls = []
            for u in users:
                def on_delete(e, u=u):
                    def confirm_delete(e):
                        if delete_user(u.code):
                            refresh_users(None)
                        page.dialog.open = False
                        page.update()

                    page.dialog = ft.AlertDialog(
                        title=ft.Text("تأكيد الحذف", text_align=ft.TextAlign.CENTER),
                        content=ft.Text("هل أنت متأكد من حذف هذا المستخدم؟", text_align=ft.TextAlign.CENTER),
                        actions=[
                            ft.TextButton("إلغاء", on_click=lambda e: setattr(page.dialog, "open", False)),
                            ft.TextButton("حذف", on_click=confirm_delete, style=ft.ButtonStyle(color=ft.Colors.RED)),
                        ],
                        actions_alignment=ft.MainAxisAlignment.CENTER,
                    )
                    page.dialog.open = True
                    page.update()

                controls.append(
                    ft.Card(
                        content=ft.Container(
                            content=ft.ResponsiveRow(
                                [
                                    ft.Column(
                                        col={"sm": 10, "md": 11},
                                        controls=[
                                            ft.Text(f"كود: {u.code}", weight=ft.FontWeight.BOLD, size=16),
                                            ft.Text(f"الاسم: {u.username}", size=14, color=ft.Colors.SECONDARY),
                                            ft.Text(f"القسم: {u.department}", size=14, color=ft.Colors.SECONDARY),
                                            ft.Text(f"الشعبة: {u.division}", size=14, color=ft.Colors.SECONDARY),
                                            ft.Text(f"الدور: {u.role}", size=14, color=ft.Colors.SECONDARY),
                                        ],
                                        alignment=ft.MainAxisAlignment.CENTER,
                                        expand=True,
                                    ),
                                    ft.Column(
                                        col={"sm": 2, "md": 1},
                                        controls=[
                                            ft.IconButton(ft.Icons.DELETE, icon_color=ft.Colors.RED, on_click=on_delete, tooltip="حذف")
                                        ],
                                        alignment=ft.MainAxisAlignment.CENTER,
                                        horizontal_alignment=ft.CrossAxisAlignment.END,
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            padding=16,
                        ),
                        elevation=3,
                    )
                )
            return controls

        user_list = ft.ListView(controls=build_user_list(), expand=True, spacing=10, padding=10)

        fields = {
            "code": ft.TextField(label="كود المستخدم"),
            "username": ft.TextField(label="اسم المستخدم"),
            "department": ft.TextField(label="القسم"),
            "division": ft.TextField(label="الشعبة"),
            "role": ft.TextField(label="الدور"),
            "password": ft.TextField(label="كلمة المرور", password=True, can_reveal_password=True),
        }

        def add_new_user(e):
            if not all(field.value for field in fields.values()):
                show_error("يرجى إدخال جميع الحقول")
                return
            if add_user(
                fields["code"].value,
                fields["username"].value,
                fields["department"].value,
                fields["division"].value,
                fields["role"].value,
                fields["password"].value,
            ):
                for field in fields.values():
                    field.value = ""
                refresh_users(None)

        form = ft.Column(
            controls=[field for field in fields.values()] + [
                ft.ElevatedButton(
                    "إضافة مستخدم",
                    on_click=add_new_user,
                    style=ft.ButtonStyle(padding=15),
                )
            ],
            spacing=10,
        )

        main_content = ft.Container(
            content=ft.Column(
                [
                    ft.Text("إدارة المستخدمين", size=24, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                    ft.Container(
                        content=form,
                        padding=16,
                        bgcolor=page.theme.color_scheme.surface,
                        border_radius=12,
                        shadow=ft.BoxShadow(blur_radius=5, color=ft.Colors.BLACK12),
                    ),
                    user_list,
                ],
                alignment=ft.MainAxisAlignment.START,
                spacing=15,
            ),
            padding=10,
            expand=True,
        )

        page.controls.clear()
        page.add(
            ft.Row(
                [
                    main_content,
                    get_navigation_rail(page.user),
                ],
                alignment=ft.MainAxisAlignment.END,
                expand=True,
            )
        )
        page.update()

    @require_login
    def show_image_viewer(url):
        main_content = ft.Container(
            content=ft.Column(
                [
                    ft.Text("عرض الصورة", size=24, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                    ft.Image(
                        src=url, 
                        fit=ft.ImageFit.CONTAIN, 
                        width=page.width - 40,
                        height=page.height - 100,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            padding=10,
            expand=True,
        )

        page.controls.clear()
        page.add(
            ft.Row(
                [
                    main_content,
                    get_navigation_rail(page.user),
                ],
                alignment=ft.MainAxisAlignment.END,
                expand=True,
            )
        )
        page.update()

    @require_login
    def show_text_viewer(url):
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                content = response.text
            else:
                content = "فشل في جلب النص"
        except Exception as e:
            content = f"خطأ: {e}"

        main_content = ft.Container(
            content=ft.Column(
                [
                    ft.Text("عرض النص", size=24, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                    ft.Container(
                        content=ft.Text(content, selectable=True, rtl=True),
                        padding=20,
                        border_radius=10,
                        bgcolor=page.theme.color_scheme.surface,
                        expand=True,
                    ),
                ],
                alignment=ft.MainAxisAlignment.START,
                spacing=15,
            ),
            padding=10,
            expand=True,
        )

        page.controls.clear()
        page.add(
            ft.Row(
                [
                    main_content,
                    get_navigation_rail(page.user),
                ],
                alignment=ft.MainAxisAlignment.END,
                expand=True,
            )
        )
        page.update()

    @require_login
    def show_home():
        main_content = ft.Container(
            content=ft.Column(
                [
                    ft.Image(
                        src="https://via.placeholder.com/150?text=Alson+Logo",
                        width=120,
                        height=120,
                        fit=ft.ImageFit.CONTAIN
                    ),
                    ft.Text(
                        "مرحباً بك في أكاديمية الألسن",
                        size=30,
                        weight=ft.FontWeight.BOLD,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.ElevatedButton(
                        "المحتوى",
                        on_click=lambda e: show_content_list(),
                        style=ft.ButtonStyle(padding=20),
                        width=200,
                    ),
                    ft.ElevatedButton(
                        "الشات",
                        on_click=lambda e: show_chat(),
                        style=ft.ButtonStyle(padding=20),
                        width=200,
                    ),
                    ft.ElevatedButton(
                        "إدارة المستخدمين",
                        on_click=lambda e: show_user_management() if page.user.role == "admin" else show_error("غير مصرح لك"),
                        style=ft.ButtonStyle(padding=20),
                        width=200,
                        visible=page.user.role == "admin",
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20,
            ),
            padding=20,
            expand=True,
        )

        page.controls.clear()
        page.add(
            ft.Row(
                [
                    main_content,
                    get_navigation_rail(page.user),
                ],
                alignment=ft.MainAxisAlignment.END,
                expand=True,
            )
        )
        page.update()

    # بدء التطبيق
    user_data = page.client_storage.get("user")
    if user_data:
        try:
            page.user = User.from_json(json.loads(user_data))
            show_home()
        except:
            login_screen()
    else:
        login_screen()

ft.app(target=main)
