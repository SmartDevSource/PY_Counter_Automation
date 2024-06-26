import pyautogui
import pyperclip
import re
import random
from customtkinter import *
from functions import *

################# DECLARATIONS #################
start_hour = ""
target = ""
has_stopped = False
incoming = None
is_active = False
is_executed = False
after_counter_id = None
after_flood_id = None
refresh_time = 5000

averages = {
    "06:00": (10,2,15),
    "06:30": (15,4,20),
    "07:00": (20,8,30),
    "07:30": (25,8,35),
    "08:00": (30,12,40),
    "08:30": (35,14,45),
    "09:00": (30,12,35),
    "09:30": (25,8,35),
    "10:00": (18,6,23),
    "10:30": (15,5,20),
    "11:00": (15,5,20)
}

################# CALL FUNCTIONS #################
def start_counter(start_hour, label):
    secs = to_seconds(start_hour)
    return count(secs, label)

def count(secs, label):
    global after_counter_id, is_executed, refresh_time, after_flood_id
    if secs > 0:
        secs -= 1
        rest = secs%3600
        hh = secs//3600
        mm = (rest//60)
        time_left = f"Exécution dans {hh:02} heure(s) et {mm+1:02} minute(s)."
        label.configure(text=time_left)
        after_counter_id = label.after(1000, count, secs, label)
    else:
        is_executed = True
        label.configure(text="Capture active")
        after_flood_id = app.after(refresh_time, get_data)

def check_hour_format():
    global start_hour
    start_hour = ipt_time.get("1.0", "end-1c")
    pattern = r'^\d{2}:\d{2}$'
    if re.match(pattern, start_hour): return True
    return False

def on_exec_click(event=None):
    global is_active, after_counter_id, after_flood_id, is_executed, refresh_time, target

    not_valid = False
    if not is_active:
        if check_hour_format():
            is_active = True
            label_counter.configure(text_color="#32CD32")
            start_counter(start_hour, label_counter)
        else:
            not_valid = True
            label_counter.configure(text="Le format d'heure est incorrect", text_color="red")
    elif is_active:
        is_active = False

    if is_active:
        btn_exec.configure(text="Stopper l'exécution", fg_color="#E50000", hover_color="#FF3131", text_color="white")
        target = ipt_direction.get("1.0", "end-1c")

    else:
        btn_exec.configure(text="Exécuter le script", fg_color="#32CD32", hover_color="#0FFF50", text_color="black")
        if not not_valid: label_counter.configure(text="")

        if after_counter_id is not None:
            label_counter.configure(text="", text_color="red")
            label_counter.after_cancel(after_counter_id)
        if after_flood_id is not None:
            app.after_cancel(after_flood_id)
            refresh_time = 5000
            is_executed = False

def on_hour_input(event):
    if is_active: return "break"
    t = ipt_time.get("1.0", "end-1c")
    if len(t) >= 5 and event.keysym != "BackSpace":
        return "break"
    
def on_terminus_input(event=None):
    global target
    target = ipt_direction.get("1.0", "end-1c")

def get_data():
    global refresh_time, target, after_flood_id, has_stopped, incoming
    pyautogui.press('f5')
    pyautogui.press('enter')
    pyautogui.hotkey('ctrl', 'a')
    pyautogui.hotkey('ctrl', 'c')

    data_pasted = pyperclip.paste().split('\n')
    data_stop = [e for e in data_pasted if "A l'arrêt" in e and target in e]
    data_incoming = [e for e in data_pasted if "A l'approche" in e and target in e]

    if len(data_incoming) == 0 and len(data_stop) == 0 and incoming is not None:
        put_data()
        incoming = None

    if len(data_incoming) > 0:
        incoming = target

    if len(data_stop) == 0 and has_stopped:
        has_stopped = False

    if len(data_stop) > 0 and not has_stopped:
        put_data()
        has_stopped = True

    after_flood_id = app.after(refresh_time, get_data)

def put_data():
        global target

        localtime = time.localtime(time.time())
        human_hour = f"{localtime.tm_hour:02}:{localtime.tm_min:02}"
        average = averages.get(round_to_half(human_hour), (20,10,20))
        get_on = random.randint(0, average[0])
        get_off = random.randint(0, average[1])
        still_in = random.randint(average[0], average[2])

        data_to_put = "_________________________________________________________________\n"
        data_to_put += f"Direction : {target}\n"
        data_to_put += f"Horaire de passage : {human_hour}\n"
        data_to_put += f"Monte : {get_on}\n"
        data_to_put += f"Descend : {get_off}\n"
        data_to_put += f"Reste : {still_in}\n"
        data_to_put += "_________________________________________________________________\n"
        data_to_put += "\n"

        with open("horaires.txt", '+a', encoding='utf-8') as file:
            file.write(data_to_put)
            file.close()

################# WINDOW INIT #################
app = CTk()
app.geometry("500x300")
set_appearance_mode("dark")
app.resizable(False, False)

################# WIDGETS #################
label_terminus = CTkLabel(master=app, 
                 text="Direction",
                 font=CTkFont(family="Arial", size=18)
                )
label_terminus.place(relx= .5, rely=.1, anchor="center")

ipt_direction = CTkTextbox(master=app,
                           height=2,
                           width=300,
                           activate_scrollbars=False,
                           border_width=1,
                           border_color="white",
                           wrap="word"
                        )
ipt_direction.place(relx= .5, rely=.2, anchor="center")
ipt_direction.bind("<Return>", lambda e: "break")
ipt_direction.bind("<KeyPress>", on_terminus_input)

label_launchtime = CTkLabel(master=app, 
                 text="Executer dans (exemple : 06:30)",
                 font=CTkFont(family="Arial", size=18)
                )
label_launchtime.place(relx= .5, rely=.35, anchor="center")

ipt_time = CTkTextbox(master=app,
                           height=2,
                           width=60,
                           activate_scrollbars=False,
                           border_width=1,
                           border_color="white",
                           wrap="word"
                        )
ipt_time.insert("end","")
ipt_time.place(relx= .5, rely=.45, anchor="center")
ipt_time.bind("<Return>", lambda e: "break")
ipt_time.bind("<KeyPress>", lambda e: on_hour_input(e))

label_counter = CTkLabel(master=app, 
                 text="",
                 font=CTkFont(family="Arial", size=18)
                )
label_counter.place(relx= .5, rely=.6, anchor="center")

btn_exec = CTkButton(master=app, 
                text="Exécuter le script", 
                corner_radius=32,
                fg_color="#32CD32",
                border_width=1,
                text_color="black",
                border_color="black",
                hover_color="#0FFF50",
                font=CTkFont(family="Arial", size=18)
            )
btn_exec.place(relx= .5, rely=.8, anchor="center")

btn_exec.bind("<Button-1>", on_exec_click)

app.bind("<Escape>", lambda e : app.quit())
app.mainloop()