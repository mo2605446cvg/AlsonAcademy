import flet as ft
import requests
import json
from user import User
from content import Content
from message import Message
import webbrowser
import os
from datetime import datetime

API_URL = "https://ki74.alalsunacademy.com/api"

def main(page: ft.Page):
    page.title = "أكاديمية الألسن"
    page.theme = ft.Theme(
        primary_color="#2196F3",
        font_family="Cairo",
        color_scheme=ft.ColorScheme(
            primary="#2196F3",
            primary_container="#E3F2FD",
            secondary="#42A5F5",
            background="#F5F5F5",
        ),
    )
    page.bgcolor = "#F5F5F5"
    page.window_width = 400
    page.window_height = 700
    page.padding = 0
    page.client_storage.clear()

    nav_rail_visible = [True]  # متغير للتحكم في إظهار/إخفاء الشريط الجانبي

    def login_user(code, password):
        if not code or not password:
            page.snack_bar = ft.SnackBar(
                content=ft.Text("يرجى إدخال كود المستخدم وكلمة المرور", rtl=True, text_align=ft.TextAlign.CENTER),
                bgcolor="#D32F2F",
                duration=3000,
            )
            page.snack_bar.open = True
            page.update()
            return None
        try:
            response = requests.post(
                f"{API_URL}/api.php?table=users&action=login",
                json={"code": code, "password": password},
                headers={"Content-Type": "application/json"},
                timeout=10,
            )
            print(f"Login Response: {response.status_code} - {response.text}")
            if response.status_code == 200:
                try:
                    user_data = response.json()
                    page.client_storage.set("user", json.dumps(user_data))
                    return User.from_json(user_data)
                except json.JSONDecodeError:
                    print(f"JSON Decode Error: {response.text}")
                    page.snack_bar = ft.SnackBar(
                        content=ft.Text("خطأ في استجابة السيرفر: تنسيق غير صالح", rtl=True),
                        bgcolor="#D32F2F",
                        duration=3000,
                    )
                    page.snack_bar.open = True
                    page.update()
                    return None
            else:
                try:
                    error_message = response.json().get("error", "خطأ غير معروف")
                except json.JSONDecodeError:
                    error_message = "خطأ في استجابة السيرفر: تنسيق غير صالح"
                page.snack_bar = ft.SnackBar(
                    content=ft.Text(error_message, rtl=True),
                    bgcolor="#D32F2F",
                    duration=3000,
                )
                page.snack_bar.open = True
                page.update()
                return None
        except Exception as e:
            print(f"Error in login_user: {e}")
            page.snack_bar = ft.SnackBar(
                content=ft.Text("فشل في الاتصال بالسيرفر: تأكد من الإنترنت", rtl=True),
                bgcolor="#D32F2F",
                duration=3000,
            )
            page.snack_bar.open = True
            page.update()
            return None

    def get_content(department, division):
        try:
            url = f"{API_URL}/api.php?table=content"
            if department and division:
                url += f"&department={department}&division={division}"
            response = requests.get(url, headers={"Content-Type": "application/json"}, timeout=10)
            print(f"Get Content Response: {response.status_code} - {response.text}")
            if response.status_code == 200:
                return [Content.from_json(item) for item in response.json()]
            else:
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("فشل في جلب المحتوى", rtl=True),
                    bgcolor="#D32F2F",
                    duration=3000,
                )
                page.snack_bar.open = True
                page.update()
                return []
        except Exception as e:
            print(f"Error in get_content: {e}")
            page.snack_bar = ft.SnackBar(
                content=ft.Text("فشل في الاتصال بالسيرفر", rtl=True),
                bgcolor="#D32F2F",
                duration=3000,
            )
            page.snack_bar.open = True
            page.update()
            return []

    def upload_content(title, file_path, uploaded_by, department, division, description):
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
                    timeout=10,
                )
                print(f"Upload Content Response: {response.status_code} - {response.text}")
                if response.status_code == 200:
                    page.snack_bar = ft.SnackBar(
                        content=ft.Text("تم رفع المحتوى بنجاح", rtl=True),
                        bgcolor="#4CAF50",
                        duration=3000,
                    )
                    page.snack_bar.open = True
                    page.update()
                else:
                    raise Exception(f"فشل في رفع المحتوى: كود الخطأ {response.status_code}")
        except Exception as e:
            print(f"Error in upload_content: {e}")
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"فشل في رفع المحتوى: {e}", rtl=True),
                bgcolor="#D32F2F",
                duration=3000,
            )
            page.snack_bar.open = True
            page.update()

    def delete_content(id):
        try:
            response = requests.delete(
                f"{API_URL}/api.php?table=content",
                json={"id": id},
                headers={"Content-Type": "application/json"},
                timeout=10,
            )
            print(f"Delete Content Response: {response.status_code}")
            if response.status_code == 200:
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("تم حذف المحتوى بنجاح", rtl=True),
                    bgcolor="#4CAF50",
                    duration=3000,
                )
                page.snack_bar.open = True
                page.update()
            else:
                raise Exception(f"فشل في حذف المحتوى: كود الخطأ {response.status_code}")
        except Exception as e:
            print(f"Error in delete_content: {e}")
            page.snack_bar = ft.SnackBar(
                content=ft.Text("فشل في الاتصال بالسيرفر", rtl=True),
                bgcolor="#D32F2F",
                duration=3000,
            )
            page.snack_bar.open = True
            page.update()

    def get_chat_messages(department, division):
        try:
            url = f"{API_URL}/api.php?table=messages"
            if department and division:
                url += f"&department={department}&division={division}"
            response = requests.get(url, headers={"Content-Type": "application/json"}, timeout=10)
            print(f"Get Messages Response: {response.status_code} - {response.text}")
            if response.status_code == 200:
                return [Message.from_json(item) for item in response.json()]
            else:
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("فشل في جلب الرسائل", rtl=True),
                    bgcolor="#D32F2F",
                    duration=3000,
                )
                page.snack_bar.open = True
                page.update()
                return []
        except Exception as e:
            print(f"Error in get_chat_messages: {e}")
            page.snack_bar = ft.SnackBar(
                content=ft.Text("فشل في الاتصال بالسيرفر", rtl=True),
                bgcolor="#D32F2F",
                duration=3000,
            )
            page.snack_bar.open = True
            page.update()
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
            print(f"Send Message Response: {response.status_code}")
            if response.status_code == 200:
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("تم إرسال الرسالة بنجاح", rtl=True),
                    bgcolor="#4CAF50",
                    duration=3000,
                )
                page.snack_bar.open = True
                page.update()
            else:
                raise Exception(f"فشل في إرسال الرسالة: كود الخطأ {response.status_code}")
        except Exception as e:
            print(f"Error in send_message: {e}")
            page.snack_bar = ft.SnackBar(
                content=ft.Text("فشل في إرسال الرسالة", rtl=True),
                bgcolor="#D32F2F",
                duration=3000,
            )
            page.snack_bar.open = True
            page.update()

    def get_users():
        try:
            response = requests.get(
                f"{API_URL}/api.php?table=users&action=all",
                headers={"Content-Type": "application/json"},
                timeout=10,
            )
            print(f"Get Users Response: {response.status_code} - {response.text}")
            if response.status_code == 200:
                return [User.from_json(item) for item in response.json()]
            else:
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("فشل في جلب المستخدمين", rtl=True),
                    bgcolor="#D32F2F",
                    duration=3000,
                )
                page.snack_bar.open = True
                page.update()
                return []
        except Exception as e:
            print(f"Error in get_users: {e}")
            page.snack_bar = ft.SnackBar(
                content=ft.Text("فشل في الاتصال بالسيرفر", rtl=True),
                bgcolor="#D32F2F",
                duration=3000,
            )
            page.snack_bar.open = True
            page.update()
            return []

    def add_user(code, username, department, division, role, password):
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
            print(f"Add User Response: {response.status_code}")
            if response.status_code == 200:
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("تم إضافة المستخدم بنجاح", rtl=True),
                    bgcolor="#4CAF50",
                    duration=3000,
                )
                page.snack_bar.open = True
                page.update()
            else:
                raise Exception(f"فشل في إضافة المستخدم: كود الخطأ {response.status_code}")
        except Exception as e:
            print(f"Error in add_user: {e}")
            page.snack_bar = ft.SnackBar(
                content=ft.Text("فشل في إضافة المستخدم", rtl=True),
                bgcolor="#D32F2F",
                duration=3000,
            )
            page.snack_bar.open = True
            page.update()

    def delete_user(code):
        try:
            response = requests.delete(
                f"{API_URL}/api.php?table=users",
                json={"code": code},
                headers={"Content-Type": "application/json"},
                timeout=10,
            )
            print(f"Delete User Response: {response.status_code}")
            if response.status_code == 200:
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("تم حذف المستخدم بنجاح", rtl=True),
                    bgcolor="#4CAF50",
                    duration=3000,
                )
                page.snack_bar.open = True
                page.update()
            else:
                raise Exception(f"فشل في حذف المستخدم: كود الخطأ {response.status_code}")
        except Exception as e:
            print(f"Error in delete_user: {e}")
            page.snack_bar = ft.SnackBar(
                content=ft.Text("فشل في حذف المستخدم", rtl=True),
                bgcolor="#D32F2F",
                duration=3000,
            )
            page.snack_bar.open = True
            page.update()

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
            print(f"Navigation changed to index: {index}")
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
                    login_screen()
            except Exception as e:
                print(f"Navigation error: {e}")
                page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"خطأ في التنقل: {e}", rtl=True),
                    bgcolor="#D32F2F",
                    duration=3000,
                )
                page.snack_bar.open = True
                page.update()

        nav_rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=100,
            bgcolor="#E3F2FD",
            indicator_color="#BBDEFB",
            destinations=destinations,
            on_change=on_nav_change,
            elevation=5,
            extended=False,
            expand=True,  # إضافة expand=True لحل مشكلة الارتفاع غير المحدد
        )

        def toggle_nav_rail(e):
            nav_rail_visible[0] = not nav_rail_visible[0]
            nav_rail_container.width = 100 if nav_rail_visible[0] else 0
            nav_rail_container.opacity = 1 if nav_rail_visible[0] else 0
            toggle_button.icon = ft.Icons.ARROW_DROP_DOWN if nav_rail_visible[0] else ft.Icons.ARROW_DROP_UP
            page.update()

        toggle_button = ft.IconButton(
            icon=ft.Icons.ARROW_DROP_DOWN,
            icon_color="#2196F3",
            on_click=toggle_nav_rail,
            tooltip="إظهار/إخفاء التنقل",
        )

        nav_rail_container = ft.Container(
            content=ft.Column(
                [
                    toggle_button,
                    nav_rail,
                ],
                alignment=ft.MainAxisAlignment.START,
                spacing=10,
            ),
            width=100,
            height=page.height,  # تحديد ارتفاع الحاوية بناءً على ارتفاع الصفحة
            bgcolor="#E3F2FD",
            border_radius=10,
            padding=10,
            animate=ft.Animation(300, ft.AnimationCurve.EASE_IN_OUT),
        )

        return nav_rail_container

    def login_screen():
        code_field = ft.TextField(
            label="كود المستخدم",
            text_align=ft.TextAlign.CENTER,
            text_style=ft.TextStyle(font_family="Cairo", size=16, color="#333333"),
            border_radius=10,
            bgcolor="#FFFFFF",
            width=300,
            rtl=True,
            border_color="#2196F3",
        )
        password_field = ft.TextField(
            label="كلمة المرور",
            password=True,
            text_align=ft.TextAlign.CENTER,
            text_style=ft.TextStyle(font_family="Cairo", size=16, color="#333333"),
            border_radius=10,
            bgcolor="#FFFFFF",
            width=300,
            rtl=True,
            border_color="#2196F3",
        )

        def on_login(e):
            user = login_user(code_field.value, password_field.value)
            if user:
                if user.role == "admin":
                    show_user_management()
                else:
                    show_content_list()

        main_content = ft.Container(
            content=ft.Column(
                [
                    ft.Image(src="https://via.placeholder.com/150?text=Alson+Logo", width=120, height=120, fit=ft.ImageFit.CONTAIN),
                    ft.Text("أكاديمية الألسن", size=30, weight=ft.FontWeight.BOLD, color="#333333", text_align=ft.TextAlign.CENTER, rtl=True),
                    ft.Container(height=20),
                    code_field,
                    ft.Container(height=10),
                    password_field,
                    ft.Container(height=20),
                    ft.ElevatedButton(
                        "تسجيل الدخول",
                        on_click=on_login,
                        style=ft.ButtonStyle(
                            padding=20,
                            bgcolor="#2196F3",
                            color="#FFFFFF",
                            shape=ft.RoundedRectangleBorder(radius=10),
                            elevation=2,
                        ),
                        width=200,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=20,
            bgcolor="#F5F5F5",
            border_radius=15,
            shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLACK12),
            alignment=ft.alignment.center,
            margin=ft.margin.all(20),
        )

        page.controls.clear()
        page.add(main_content)
        page.update()

    def show_content_list():
        user_json = page.client_storage.get("user")
        user = User.from_json(json.loads(user_json)) if user_json else None
        if not user:
            login_screen()
            return

        content = get_content(user.department, user.division)

        def refresh_content(e):
            nonlocal content
            content = get_content(user.department, user.division)
            content_list.controls = build_content_list()
            page.update()

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
                        delete_content(item.id)
                        refresh_content(None)
                        page.dialog.open = False
                        page.update()

                    page.dialog = ft.AlertDialog(
                        title=ft.Text("تأكيد الحذف", text_align=ft.TextAlign.CENTER, style=ft.TextStyle(font_family="Cairo", size=16, color="#333333"), rtl=True),
                        content=ft.Text("هل أنت متأكد من حذف هذا المحتوى؟", text_align=ft.TextAlign.CENTER, style=ft.TextStyle(font_family="Cairo", size=14), rtl=True),
                        actions=[
                            ft.TextButton("إلغاء", on_click=lambda e: setattr(page.dialog, "open", False)),
                            ft.TextButton("حذف", on_click=confirm_delete, style=ft.ButtonStyle(color="#D32F2F")),
                        ],
                        actions_alignment=ft.MainAxisAlignment.CENTER,
                    )
                    page.dialog.open = True
                    page.update()

                actions = [
                    ft.IconButton(ft.Icons.VISIBILITY, icon_color="#2196F3", on_click=lambda e: on_view(e, item), tooltip="عرض"),
                ]
                if user.role == "admin":
                    actions.append(ft.IconButton(ft.Icons.DELETE, icon_color="#D32F2F", on_click=lambda e: on_delete(e, item), tooltip="حذف"))

                controls.append(
                    ft.Card(
                        content=ft.Container(
                            content=ft.Row(
                                [
                                    ft.Column(
                                        [
                                            ft.Text(item.title, weight=ft.FontWeight.BOLD, size=16, color="#333333", rtl=True),
                                            ft.Text(f"نوع الملف: {item.file_type}", size=14, color="#666666", rtl=True),
                                            ft.Text(f"تم الرفع بواسطة: {item.uploaded_by}", size=14, color="#666666", rtl=True),
                                            ft.Text(f"تاريخ الرفع: {item.upload_date}", size=14, color="#666666", rtl=True),
                                            ft.Text(f"نبذة: {item.description}", size=14, color="#666666", rtl=True, max_lines=2, overflow=ft.TextOverflow.ELLIPSIS),
                                        ],
                                        alignment=ft.MainAxisAlignment.CENTER,
                                        expand=True,
                                    ),
                                    ft.Column(actions, alignment=ft.MainAxisAlignment.CENTER),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            padding=16,
                        ),
                        elevation=3,
                        color="#FFFFFF",
                        margin=ft.margin.only(left=10, right=10, top=5, bottom=5),
                    )
                )
            return controls

        content_list = ft.ListView(controls=build_content_list(), expand=True, spacing=10, padding=10)

        main_content = ft.Container(
            content=ft.Column(
                [
                    ft.Text("المحتوى", size=24, weight=ft.FontWeight.BOLD, color="#333333", text_align=ft.TextAlign.CENTER, rtl=True),
                    ft.ElevatedButton(
                        "تحديث المحتوى",
                        on_click=refresh_content,
                        style=ft.ButtonStyle(
                            padding=15,
                            bgcolor="#2196F3",
                            color="#FFFFFF",
                            shape=ft.RoundedRectangleBorder(radius=10),
                            elevation=2,
                        ),
                    ),
                    content_list,
                ],
                alignment=ft.MainAxisAlignment.START,
                spacing=15,
            ),
            padding=10,
            bgcolor="#F5F5F5",
        )

        page.controls.clear()
        page.add(
            ft.Row(
                [
                    ft.Container(
                        content=main_content,
                        expand=True,
                        padding=10,
                        bgcolor="#F5F5F5",
                    ),
                    get_navigation_rail(user),
                ],
                alignment=ft.MainAxisAlignment.END,
                expand=True,
            )
        )
        page.update()

    def show_content_upload():
        user_json = page.client_storage.get("user")
        user = User.from_json(json.loads(user_json)) if user_json else None
        if not user or user.role != "admin":
            page.snack_bar = ft.SnackBar(
                content=ft.Text("غير مصرح لك برفع المحتوى", rtl=True),
                bgcolor="#D32F2F",
                duration=3000,
            )
            page.snack_bar.open = True
            login_screen()
            return

        title_field = ft.TextField(
            label="عنوان المحتوى",
            text_align=ft.TextAlign.CENTER,
            text_style=ft.TextStyle(font_family="Cairo", size=16, color="#333333"),
            border_radius=10,
            bgcolor="#FFFFFF",
            width=300,
            rtl=True,
            border_color="#2196F3",
        )
        description_field = ft.TextField(
            label="نبذة عن المحتوى",
            text_align=ft.TextAlign.CENTER,
            text_style=ft.TextStyle(font_family="Cairo", size=16, color="#333333"),
            border_radius=10,
            bgcolor="#FFFFFF",
            width=300,
            rtl=True,
            border_color="#2196F3",
        )
        file_name = ft.Text("لم يتم اختيار ملف", text_align=ft.TextAlign.CENTER, style=ft.TextStyle(font_family="Cairo", size=14, color="#333333"), rtl=True)
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
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("يرجى إدخال العنوان، النبذة، واختيار ملف", rtl=True),
                    bgcolor="#D32F2F",
                    duration=3000,
                )
                page.snack_bar.open = True
                page.update()
                return
            upload_content(title_field.value, file_path[0], user.code, user.department, user.division, description_field.value)
            title_field.value = ""
            description_field.value = ""
            file_name.value = "لم يتم اختيار ملف"
            file_path[0] = None
            show_content_list()

        main_content = ft.Container(
            content=ft.Column(
                [
                    ft.Text("رفع محتوى", size=24, weight=ft.FontWeight.BOLD, color="#333333", text_align=ft.TextAlign.CENTER, rtl=True),
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
                                    style=ft.ButtonStyle(
                                        padding=15,
                                        bgcolor="#2196F3",
                                        color="#FFFFFF",
                                        shape=ft.RoundedRectangleBorder(radius=10),
                                        elevation=2,
                                    ),
                                ),
                                file_name,
                                ft.Container(height=16),
                                ft.ElevatedButton(
                                    "رفع المحتوى",
                                    on_click=upload,
                                    style=ft.ButtonStyle(
                                        padding=15,
                                        bgcolor="#2196F3",
                                        color="#FFFFFF",
                                        shape=ft.RoundedRectangleBorder(radius=10),
                                        elevation=2,
                                    ),
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                        padding=16,
                        bgcolor="#FFFFFF",
                        border_radius=12,
                        border=ft.border.all(color="#2196F3", width=1),
                        shadow=ft.BoxShadow(blur_radius=5, color=ft.Colors.BLACK12),
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=20,
            ),
            padding=20,
            bgcolor="#F5F5F5",
        )

        page.controls.clear()
        page.add(
            ft.Row(
                [
                    ft.Container(
                        content=main_content,
                        expand=True,
                        padding=10,
                        bgcolor="#F5F5F5",
                    ),
                    get_navigation_rail(user),
                ],
                alignment=ft.MainAxisAlignment.END,
                expand=True,
            )
        )
        page.update()

    def show_chat():
        user_json = page.client_storage.get("user")
        user = User.from_json(json.loads(user_json)) if user_json else None
        if not user:
            login_screen()
            return

        message_field = ft.TextField(
            label="اكتب رسالتك...",
            text_align=ft.TextAlign.RIGHT,
            text_style=ft.TextStyle(font_family="Cairo", size=16, color="#333333"),
            border_radius=30,
            bgcolor="#FFFFFF",
            width=300,
            rtl=True,
            border_color="#2196F3",
        )
        messages = get_chat_messages(user.department, user.division)

        def refresh_messages(e):
            nonlocal messages
            messages = get_chat_messages(user.department, user.division)
            chat_list.controls = build_chat_list()
            page.update()

        def send(e):
            if not message_field.value:
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("يرجى إدخال رسالة", rtl=True),
                    bgcolor="#D32F2F",
                    duration=3000,
                )
                page.snack_bar.open = True
                page.update()
                return
            send_message(user.code, user.department, user.division, message_field.value)
            message_field.value = ""
            refresh_messages(None)

        def build_chat_list():
            controls = []
            for message in reversed(messages):
                is_me = message.sender_id == user.code
                controls.append(
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text(
                                    message.username,
                                    weight=ft.FontWeight.BOLD,
                                    color="#FFFFFF" if is_me else "#333333",
                                    size=14,
                                    rtl=True,
                                ),
                                ft.Text(
                                    message.content,
                                    color="#FFFFFF" if is_me else "#333333",
                                    size=16,
                                    rtl=True,
                                    max_lines=10,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                ),
                                ft.Text(
                                    message.timestamp,
                                    size=12,
                                    color="#E3F2FD" if is_me else "#666666",
                                    rtl=True,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.START,
                            spacing=5,
                        ),
                        padding=ft.padding.only(left=12, right=12, top=8, bottom=8),
                        margin=ft.margin.only(left=16 if is_me else 80, right=80 if is_me else 16, top=4, bottom=4),
                        bgcolor="#DCF8C6" if is_me else "#FFFFFF",
                        border_radius=15,
                        border=ft.border.all(color="#2196F3" if is_me else "#E0E0E0", width=1),
                        alignment=ft.Alignment(1, 0) if is_me else ft.Alignment(-1, 0),
                        shadow=ft.BoxShadow(blur_radius=3, color=ft.Colors.BLACK12),
                    )
                )
            return controls

        chat_list = ft.ListView(controls=build_chat_list(), expand=True, reverse=True, spacing=10, padding=10)

        main_content = ft.Container(
            content=ft.Column(
                [
                    ft.Text("الشات", size=24, weight=ft.FontWeight.BOLD, color="#333333", text_align=ft.TextAlign.CENTER, rtl=True),
                    ft.ElevatedButton(
                        "تحديث الرسائل",
                        on_click=refresh_messages,
                        style=ft.ButtonStyle(
                            padding=15,
                            bgcolor="#2196F3",
                            color="#FFFFFF",
                            shape=ft.RoundedRectangleBorder(radius=10),
                            elevation=2,
                        ),
                    ),
                    chat_list,
                    ft.Row(
                        [
                            message_field,
                            ft.IconButton(
                                ft.Icons.SEND,
                                icon_color="#2196F3",
                                on_click=send,
                                tooltip="إرسال",
                                bgcolor="#FFFFFF",
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
            bgcolor="#F5F5F5",
        )

        page.controls.clear()
        page.add(
            ft.Row(
                [
                    ft.Container(
                        content=main_content,
                        expand=True,
                        padding=10,
                        bgcolor="#F5F5F5",
                    ),
                    get_navigation_rail(user),
                ],
                alignment=ft.MainAxisAlignment.END,
                expand=True,
            )
        )
        page.update()

    def show_user_management():
        user_json = page.client_storage.get("user")
        user = User.from_json(json.loads(user_json)) if user_json else None
        if not user or user.role != "admin":
            page.snack_bar = ft.SnackBar(
                content=ft.Text("غير مصرح لك بإدارة المستخدمين", rtl=True),
                bgcolor="#D32F2F",
                duration=3000,
            )
            page.snack_bar.open = True
            login_screen()
            return

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
                        delete_user(u.code)
                        refresh_users(None)
                        page.dialog.open = False
                        page.update()

                    page.dialog = ft.AlertDialog(
                        title=ft.Text("تأكيد الحذف", text_align=ft.TextAlign.CENTER, style=ft.TextStyle(font_family="Cairo", size=16, color="#333333"), rtl=True),
                        content=ft.Text("هل أنت متأكد من حذف هذا المستخدم؟", text_align=ft.TextAlign.CENTER, style=ft.TextStyle(font_family="Cairo", size=14), rtl=True),
                        actions=[
                            ft.TextButton("إلغاء", on_click=lambda e: setattr(page.dialog, "open", False)),
                            ft.TextButton("حذف", on_click=confirm_delete, style=ft.ButtonStyle(color="#D32F2F")),
                        ],
                        actions_alignment=ft.MainAxisAlignment.CENTER,
                    )
                    page.dialog.open = True
                    page.update()

                controls.append(
                    ft.Card(
                        content=ft.Container(
                            content=ft.Row(
                                [
                                    ft.Column(
                                        [
                                            ft.Text(f"كود: {u.code}", weight=ft.FontWeight.BOLD, size=16, color="#333333", rtl=True),
                                            ft.Text(f"الاسم: {u.username}", size=14, color="#666666", rtl=True),
                                            ft.Text(f"القسم: {u.department}", size=14, color="#666666", rtl=True),
                                            ft.Text(f"الشعبة: {u.division}", size=14, color="#666666", rtl=True),
                                            ft.Text(f"الدور: {u.role}", size=14, color="#666666", rtl=True),
                                        ],
                                        alignment=ft.MainAxisAlignment.CENTER,
                                        expand=True,
                                    ),
                                    ft.IconButton(ft.Icons.DELETE, icon_color="#D32F2F", on_click=lambda e: on_delete(e, u), tooltip="حذف"),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            padding=16,
                        ),
                        elevation=3,
                        color="#FFFFFF",
                        margin=ft.margin.only(left=10, right=10, top=5, bottom=5),
                    )
                )
            return controls

        user_list = ft.ListView(controls=build_user_list(), expand=True, spacing=10, padding=10)

        code_field = ft.TextField(
            label="كود المستخدم",
            text_align=ft.TextAlign.CENTER,
            text_style=ft.TextStyle(font_family="Cairo", size=16, color="#333333"),
            border_radius=10,
            bgcolor="#FFFFFF",
            width=300,
            rtl=True,
            border_color="#2196F3",
        )
        username_field = ft.TextField(
            label="اسم المستخدم",
            text_align=ft.TextAlign.CENTER,
            text_style=ft.TextStyle(font_family="Cairo", size=16, color="#333333"),
            border_radius=10,
            bgcolor="#FFFFFF",
            width=300,
            rtl=True,
            border_color="#2196F3",
        )
        department_field = ft.TextField(
            label="القسم",
            text_align=ft.TextAlign.CENTER,
            text_style=ft.TextStyle(font_family="Cairo", size=16, color="#333333"),
            border_radius=10,
            bgcolor="#FFFFFF",
            width=300,
            rtl=True,
            border_color="#2196F3",
        )
        division_field = ft.TextField(
            label="الشعبة",
            text_align=ft.TextAlign.CENTER,
            text_style=ft.TextStyle(font_family="Cairo", size=16, color="#333333"),
            border_radius=10,
            bgcolor="#FFFFFF",
            width=300,
            rtl=True,
            border_color="#2196F3",
        )
        role_field = ft.TextField(
            label="الدور",
            text_align=ft.TextAlign.CENTER,
            text_style=ft.TextStyle(font_family="Cairo", size=16, color="#333333"),
            border_radius=10,
            bgcolor="#FFFFFF",
            width=300,
            rtl=True,
            border_color="#2196F3",
        )
        password_field = ft.TextField(
            label="كلمة المرور",
            password=True,
            text_align=ft.TextAlign.CENTER,
            text_style=ft.TextStyle(font_family="Cairo", size=16, color="#333333"),
            border_radius=10,
            bgcolor="#FFFFFF",
            width=300,
            rtl=True,
            border_color="#2196F3",
        )

        def add_new_user(e):
            if not all([code_field.value, username_field.value, department_field.value, division_field.value, role_field.value, password_field.value]):
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("يرجى إدخال جميع الحقول", rtl=True),
                    bgcolor="#D32F2F",
                    duration=3000,
                )
                page.snack_bar.open = True
                page.update()
                return
            add_user(
                code_field.value,
                username_field.value,
                department_field.value,
                division_field.value,
                role_field.value,
                password_field.value,
            )
            code_field.value = ""
            username_field.value = ""
            department_field.value = ""
            division_field.value = ""
            role_field.value = ""
            password_field.value = ""
            refresh_users(None)

        main_content = ft.Container(
            content=ft.Column(
                [
                    ft.Text("إدارة المستخدمين", size=24, weight=ft.FontWeight.BOLD, color="#333333", text_align=ft.TextAlign.CENTER, rtl=True),
                    ft.Container(
                        content=ft.Column(
                            [
                                code_field,
                                username_field,
                                department_field,
                                division_field,
                                role_field,
                                password_field,
                                ft.ElevatedButton(
                                    "إضافة مستخدم",
                                    on_click=add_new_user,
                                    style=ft.ButtonStyle(
                                        padding=15,
                                        bgcolor="#2196F3",
                                        color="#FFFFFF",
                                        shape=ft.RoundedRectangleBorder(radius=10),
                                        elevation=2,
                                    ),
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=10,
                        ),
                        padding=16,
                        bgcolor="#FFFFFF",
                        border_radius=12,
                        border=ft.border.all(color="#2196F3", width=1),
                        shadow=ft.BoxShadow(blur_radius=5, color=ft.Colors.BLACK12),
                    ),
                    user_list,
                ],
                alignment=ft.MainAxisAlignment.START,
                spacing=15,
            ),
            padding=10,
            bgcolor="#F5F5F5",
        )

        page.controls.clear()
        page.add(
            ft.Row(
                [
                    ft.Container(
                        content=main_content,
                        expand=True,
                        padding=10,
                        bgcolor="#F5F5F5",
                    ),
                    get_navigation_rail(user),
                ],
                alignment=ft.MainAxisAlignment.END,
                expand=True,
            )
        )
        page.update()

    def show_image_viewer(url):
        user_json = page.client_storage.get("user")
        user = User.from_json(json.loads(user_json)) if user_json else None
        if not user:
            login_screen()
            return

        main_content = ft.Container(
            content=ft.Column(
                [
                    ft.Text("عرض الصورة", size=24, weight=ft.FontWeight.BOLD, color="#333333", text_align=ft.TextAlign.CENTER, rtl=True),
                    ft.Image(src=url, fit=ft.ImageFit.CONTAIN, width=page.width - 20, height=page.height - 100),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            padding=10,
            bgcolor="#F5F5F5",
        )

        page.controls.clear()
        page.add(
            ft.Row(
                [
                    ft.Container(
                        content=main_content,
                        expand=True,
                        padding=10,
                        bgcolor="#F5F5F5",
                    ),
                    get_navigation_rail(user),
                ],
                alignment=ft.MainAxisAlignment.END,
                expand=True,
            )
        )
        page.update()

    def show_text_viewer(url):
        user_json = page.client_storage.get("user")
        user = User.from_json(json.loads(user_json)) if user_json else None
        if not user:
            login_screen()
            return

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
                    ft.Text("عرض النص", size=24, weight=ft.FontWeight.BOLD, color="#333333", text_align=ft.TextAlign.CENTER, rtl=True),
                    ft.Text(content, style=ft.TextStyle(font_family="Cairo", size=16, color="#333333"), selectable=True, rtl=True),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=15,
            ),
            padding=10,
            bgcolor="#F5F5F5",
        )

        page.controls.clear()
        page.add(
            ft.Row(
                [
                    ft.Container(
                        content=main_content,
                        expand=True,
                        padding=10,
                        bgcolor="#F5F5F5",
                    ),
                    get_navigation_rail(user),
                ],
                alignment=ft.MainAxisAlignment.END,
                expand=True,
            )
        )
        page.update()

    def show_home():
        user_json = page.client_storage.get("user")
        user = User.from_json(json.loads(user_json)) if user_json else None
        if not user:
            login_screen()
            return

        main_content = ft.Container(
            content=ft.Column(
                [
                    ft.Image(src="https://via.placeholder.com/150?text=Alson+Logo", width=120, height=120, fit=ft.ImageFit.CONTAIN),
                    ft.Text("مرحباً بك في أكاديمية الألسن", size=30, weight=ft.FontWeight.BOLD, color="#333333", text_align=ft.TextAlign.CENTER, rtl=True),
                    ft.ElevatedButton(
                        "المحتوى",
                        on_click=lambda e: show_content_list(),
                        style=ft.ButtonStyle(
                            padding=20,
                            bgcolor="#2196F3",
                            color="#FFFFFF",
                            shape=ft.RoundedRectangleBorder(radius=10),
                            elevation=2,
                        ),
                        width=200,
                    ),
                    ft.ElevatedButton(
                        "الشات",
                        on_click=lambda e: show_chat(),
                        style=ft.ButtonStyle(
                            padding=20,
                            bgcolor="#2196F3",
                            color="#FFFFFF",
                            shape=ft.RoundedRectangleBorder(radius=10),
                            elevation=2,
                        ),
                        width=200,
                    ),
                    ft.ElevatedButton(
                        "إدارة المستخدمين",
                        on_click=lambda e: show_user_management() if user.role == "admin" else (
                            setattr(page, "snack_bar", ft.SnackBar(
                                content=ft.Text("غير مصرح لك بإدارة المستخدمين", rtl=True),
                                bgcolor="#D32F2F",
                                duration=3000,
                            )) or setattr(page.snack_bar, "open", True) or page.update()
                        ),
                        style=ft.ButtonStyle(
                            padding=20,
                            bgcolor="#2196F3",
                            color="#FFFFFF",
                            shape=ft.RoundedRectangleBorder(radius=10),
                            elevation=2,
                        ),
                        width=200,
                        visible=user.role == "admin",
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20,
            ),
            padding=20,
            bgcolor="#F5F5F5",
        )

        page.controls.clear()
        page.add(
            ft.Row(
                [
                    ft.Container(
                        content=main_content,
                        expand=True,
                        padding=10,
                        bgcolor="#F5F5F5",
                    ),
                    get_navigation_rail(user),
                ],
                alignment=ft.MainAxisAlignment.END,
                expand=True,
            )
        )
        page.update()

    user_json = page.client_storage.get("user")
    if user_json:
        user = User.from_json(json.loads(user_json))
        if user.role == "admin":
            show_user_management()
        else:
            show_content_list()
    else:
        login_screen()

ft.app(target=main)