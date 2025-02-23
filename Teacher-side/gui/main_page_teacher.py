from customtkinter import CTk, CTkButton, CTkFrame, CTkLabel, CTkEntry, NORMAL, DISABLED, END
from tkinter import ttk, CENTER, BOTH, RIGHT, Y, VERTICAL
from pathlib import Path
import sys
from threading import Thread
from ping3 import ping

parent_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_dir / "backend"))

from get_students import get_students_list, fetch_messages

class MainPage(CTk):
    def __init__(self, class_id):
        super().__init__()

        self.class_id = class_id
        self.student_rows = {}
        self.students_list = [False, 'NotAssigned']

        self.title("Main Page")
        self.geometry('900x600')
        self.minsize(900, 600)
        # main red frame
        self.main_frame = CTkFrame(master=self, border_color='red', border_width=2)
        self.main_frame.pack(padx=20, pady=20, expand=True, fill='both')
        
        #elements frame for holding everything in center 
        self.element_frame = CTkFrame(master=self.main_frame, fg_color='transparent')
        self.element_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        ## Adding Table ##
        # Creating Treeview (Table)
        self.table = ttk.Treeview(
            master=self.element_frame,
            columns=("Name", "Last Check result & Time", "Accuracy rate", "Desktop"),
            show='headings',
            height=15
        )
        Thread(target=self.get_students_list).start()


        # Defining Columns
        for col in ("Name", "Last Check result & Time", "Accuracy rate", "Desktop"):
            self.table.heading(col, text=col, anchor=CENTER)
            if col == 'Name' :
                self.table.column(col, anchor=CENTER, width=160)
            else:
                self.table.column(col, anchor=CENTER, width=80)
            self.table.column('Last Check result & Time', anchor=CENTER, width=200)


        # Adding Scrollbar
        self.scrollbar = ttk.Scrollbar(self.element_frame, orient=VERTICAL, command=self.table.yview)
        self.table.configure(yscrollcommand=self.scrollbar.set)

        # Placing Table and Scrollbar
        self.table.grid(row=1, column=0, pady=20, columnspan=2, sticky='we')
        self.scrollbar.grid(row=1, column=1, sticky='nes', pady=20)

        # elements 
        self.main_label = CTkLabel(master=self.element_frame, text=f'Students Class {self.class_id} Status', font=('montserrat', 30, 'bold'))
        self.ping_lbl = CTkLabel(master=self.element_frame, text='PING', font=('montserrat', 25, 'bold'))
        self.ping_entry = CTkEntry(master=self.element_frame, height=40, width=130, font=('montserrat', 20, 'bold'), fg_color='#2B2B2B', border_color='#2B2B2B', justify='right')
        self.exit_button = CTkButton(master=self.element_frame, text='Exit', font=('montserrat', 20, 'bold'), height=30, width=250, fg_color='red', hover_color='#6B0011', border_color='white', border_width=2, command=lambda: self.destroy())

        # placing elements in element_frame      
        self.main_label.grid(row=0, column=0 ,sticky='n', columnspan=2)
        self.exit_button.grid(row=3, column=0, pady=(10,0), sticky='we', columnspan=2)
        self.ping_lbl.grid(row=2, column=0, sticky='w')
        self.ping_entry.grid(row=2, column=1, sticky='e')

        self.ping_entry.configure(state=DISABLED)
        Thread(target=self.pinging).start()



    def pinging(self):
        try:
            response_time = ping('google.com', unit='ms')
            if response_time is not None:
                response_time = f"{response_time:.2f} ms"
            else:
                response_time = f"Failed"

            if response_time:
                self.ping_entry.configure(state=NORMAL)
                self.ping_entry.delete(0, END)
                self.ping_entry.insert(END, response_time)
            else:
                response_time == 'Failed'
                self.ping_entry.configure(state=NORMAL)
                self.ping_entry.delete(0, END)
                self.ping_entry.insert(END, response_time)
            self.ping_entry.configure(state=DISABLED)
        except Exception:
            self.ping_entry.configure(state=NORMAL)
            self.ping_entry.delete(0, END)
            self.ping_entry.insert(END, 'ERROR')            
            self.ping_entry.configure(state=DISABLED)
        self.after(1000, self.pinging)

    def get_students_list(self):
        print('trying yo get ...')
        self.students_list = get_students_list(school_name=str(self.class_id).split('-')[0], class_code=str(self.class_id).split('-')[1])
        print('i got it')
        if self.students_list[0]:
            print('here')
            Thread(target=self.set_students_int_table, daemon=True).start()
        else:
            print(f'--------------------\nERROR IS : \n{self.students_list[1]}\n--------------------')
            self.after(30000, self.get_students_list)

    def set_students_int_table(self):

        if self.students_list[0] :
            # self.students_list = self.students_list[1]
            for student in self.students_list[1]:
                item_id = self.table.insert("", "end", values=(student, 'N/A', 'N/A', 'N/A'))
                self.student_rows[student] = item_id 
            Thread(target=self.update_data, daemon=True).start()
        else:
            print(f'ERROR : {self.students_list[1]}')
            self.after(30000, self.set_students_int_table)


    def update_data(self):
        def update_data_thread_handler():
            print('--new round started')
            if self.students_list[0]:
                for student in self.students_list[1] :
                    print(f'im going to get message of {student}...')
                    respond = fetch_messages(student=student, school_name=str(self.class_id).split('-')[0], class_code=str(self.class_id).split('-')[1])
                    if respond[0] :
                        code, time = str(respond[1]).split('-')[0], str(respond[1]).split('-')[1] 
                        if code == '1':
                            final_message = f'Students goes-{time}'
                        elif code == '2' :
                            final_message = f'Identity not confirmed-{time}'
                        elif code == '3' :
                            final_message = f'Sleeping-{time}'
                        elif code == '4':
                            final_message = f'Not looking-{time}'
                        elif code == '5' :
                            final_message = f'Looking-{time}'
                        elif code == 'True' : 
                            final_message = f'Fucking looking-{time}'
                        
                        self.table.item(self.student_rows[student], values=(student, final_message, "N/A", "N/A"))
                    else:
                        print('Connection Error while getting last message')
            else:
                print('an Error occured while getting studdents list')
        Thread(target=update_data_thread_handler).start()
        self.after(30000, self.update_data)


    def run(self):
        self.mainloop()


def main_page_func_teacher(classid):
    app = MainPage(classid)
    app.run()


if __name__ == '__main__' : 
    main_page_func_teacher('hn1-1052')
