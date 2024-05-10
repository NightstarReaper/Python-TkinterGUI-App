import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

DATA_FILE = 'video.txt'
CUSTOMER_DATA_FILE = 'customer.txt'


class TabbedApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Tabbed App")

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True)

    def add_tab(self, tab_class, tab_name):
        tab_frame = ttk.Frame(self.notebook)
        tab_instance = tab_class(tab_frame)
        self.notebook.add(tab_frame, text=tab_name)

    def run(self):
        self.root.mainloop()


class VideoInfoApp:
    def __init__(self, root):
        self.root = root
        self.customer_data = {'ID': [], 'First Name': [], 'Last Name': [], 'Address': [], 'Phone Number': [],
                              'Email Address': []}
        self.video_data = {'ID': [], 'Name': [], 'Year': [], 'Director': [], 'Rating': [], 'Genre': [], 'Status': []}
        self.rental_data = []  # List to store rental information
        self.initialize_ui()
        self.load_data_from_file()
        self.sort_order = {}  # To keep track of the sorting order for each column

    def initialize_ui(self):
        style = ttk.Style()
        style.theme_use('clam')

        # Light theme color configuration
        bg_color = '#FFFFFF'
        fg_color = '#333333'
        button_color = '#E0E0E0'
        button_hover = '#CCCCCC'
        rent_button_color = '#FF3B30'
        return_button_color = '#34C759'
        text_color_on_buttons = '#FFFFFF'

        # Configure the style for the overall frame, buttons, labels, and treeview
        style.configure('TFrame', background=bg_color)
        style.configure('TButton', font=('Helvetica', 10), background=button_color, foreground=fg_color)
        style.map('TButton', background=[('active', button_hover)], foreground=[('active', fg_color)])
        style.configure('TLabel', font=('Helvetica', 10), background=bg_color, foreground=fg_color)
        style.configure('Treeview', font=('Helvetica', 10), background=bg_color, fieldbackground=bg_color,
                        foreground=fg_color)
        style.configure('Treeview.Heading', font=('Helvetica', 10, 'bold'), background=button_color,
                        foreground=fg_color)

        # Custom styles for Rent and Return buttons
        style.configure('TRentButton.TButton', background=rent_button_color, foreground=text_color_on_buttons)
        style.map('TRentButton.TButton', background=[('active', rent_button_color)],
                  foreground=[('active', text_color_on_buttons)])
        style.configure('TReturnButton.TButton', background=return_button_color, foreground=text_color_on_buttons)
        style.map('TReturnButton.TButton', background=[('active', return_button_color)],
                  foreground=[('active', text_color_on_buttons)])

        self.rent_button = ttk.Button(self.root, text="Rent Movie", style='TRentButton.TButton',
                                      command=self.create_rent_popup)
        self.rent_button.grid(row=4, column=0, padx=10, pady=5, sticky='EW')

        self.manage_video_label = ttk.Label(self.root, text="Manage Video", font=("Helvetica", 16, "bold"),
                                            background=bg_color, foreground=fg_color)
        self.manage_video_label.grid(row=0, column=0, columnspan=4, padx=10, pady=10, sticky='W')

        self.search_label = ttk.Label(self.root, text="Movie Name Search", background=bg_color, foreground=fg_color)
        self.search_label.grid(row=1, column=0, padx=5, pady=0, sticky='EW')

        self.search_entry = ttk.Entry(self.root, width=20)
        self.search_entry.grid(row=2, column=0, padx=5, pady=5, sticky='EW')

        self.search_button = ttk.Button(self.root, text="Search", command=self.search_video)
        self.search_button.grid(row=2, column=1, padx=5, pady=5, sticky='EW')

        self.sort_label = ttk.Label(self.root, text="Sort:")
        self.sort_label.grid(row=2, column=2, padx=5, pady=5, sticky='EW')

        self.sort_var = tk.StringVar()
        self.sort_options = ['ID', 'Name', 'Year', 'Director', 'Rating', 'Genre', 'Status']
        self.sort_menu = tk.OptionMenu(self.root, self.sort_var, *self.sort_options, command=self.on_sort_selection)
        self.sort_menu.grid(row=2, column=3, padx=5, pady=5, sticky='EW')

        self.open_add_window_button = ttk.Button(self.root, text="Add New Video", command=self.create_add_window)
        self.open_add_window_button.grid(row=2, column=4, padx=10, pady=10, sticky='EW')

        # Create and configure the Treeview for displaying video data
        self.tree = ttk.Treeview(self.root, columns=list(self.video_data.keys()) + ['Edit', 'Delete'], show='headings')
        for col in self.video_data.keys():
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        self.tree.column('Edit', width=60, anchor='center')
        self.tree.column('Delete', width=60, anchor='center')

        self.populate_treeview_with_data()
        self.tree.grid(row=3, column=0, columnspan=4, padx=10, pady=10, sticky='NSEW')

        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(3, weight=1)

        self.rent_button = ttk.Button(self.root, text="Rent Movie", style='TRentButton.TButton',
                                      command=self.open_rent_movie_popup)
        self.rent_button.grid(row=4, column=0, padx=10, pady=5, sticky='EW')

        self.return_button = ttk.Button(self.root, text="Return Movie", style='TReturnButton.TButton',
                                        command=self.return_movie)
        self.return_button.grid(row=4, column=1, padx=10, pady=5, sticky='EW')

        separator = ttk.Separator(self.root, orient='horizontal')
        separator.grid(row=5, column=0, columnspan=4, sticky="ew", pady=10)

        # Add headings for Edit/Delete
        self.tree.heading('Edit', text='Edit')
        self.tree.heading('Delete', text='Delete')

        self.tree.bind("<ButtonRelease-1>", self.on_treeview_click)

    def open_rent_movie_popup(self):
        # Check if a movie is selected in the Treeview
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a movie to rent.")
            return

        # Create a popup window for renting the movie
        rent_window = tk.Toplevel(self.root)
        rent_window.title("Rent Movie")

        # Create a label for selecting a customer
        customer_label = ttk.Label(rent_window, text="Select a Customer:")
        customer_label.grid(row=0, column=0, padx=10, pady=5)

        # Create a Treeview for displaying customer data
        customer_tree = ttk.Treeview(rent_window, columns=list(self.customer_data.keys()))
        for col in self.customer_data.keys():
            customer_tree.heading(col, text=col)
            customer_tree.column(col, width=100)

        customer_tree.grid(row=1, column=0, padx=10, pady=5)

        # Populate the customer Treeview with data
        self.populate_customer_treeview(customer_tree)

        # Create a button to confirm the movie rental for the selected customer
        rent_button = ttk.Button(rent_window, text="Rent",
                                 command=lambda: self.confirm_rental(selected_item, customer_tree, rent_window))
        rent_button.grid(row=2, column=0, padx=10, pady=10)

    def show_tree_menu(self, event):
        # Check if there's an item under the cursor
        iid = self.tree.identify_row(event.y)
        if iid:
            # Change the selection to the right-clicked item
            self.tree.selection_set(iid)
            self.tree_menu.post(event.x_root, event.y_root)

    def delete_selected_item(self):
        selected_item = self.tree.selection()[0]
        # Code to delete the selected item goes here
        print(f"Delete item {selected_item}")

    def rent_movie(self):
        selected_item = self.tree.selection()[0]
        movie_id = self.tree.item(selected_item, 'values')[0]
        index = self.video_data['ID'].index(movie_id)
        self.video_data['Status'][index] = 'Rented'
        self.update_treeview()
        self.save_data_to_file()

    def populate_customer_treeview(self, tree):
        for item in tree.get_children():
            tree.delete(item)

        for i in range(len(self.customer_data['ID'])):
            row_data = [self.customer_data[key][i] for key in self.customer_data.keys()]
            tree.insert("", "end", values=row_data)

    def return_movie(self):
        selected_item = self.tree.selection()[0]
        movie_id = self.tree.item(selected_item, 'values')[0]
        index = self.video_data['ID'].index(movie_id)
        self.video_data['Status'][index] = 'Available'
        self.update_treeview()
        self.save_data_to_file()

    def add_customer_to_treeview(self, entries, add_window):
        # Validate phone number
        if not self.validate_phone_number(entries[4]):  # Assuming phone number is the 5th entry
            print("Invalid phone number. Must be 10 digits.")
            return

    def update_treeview(self):
        # Clear the existing Treeview entries
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Repopulate the Treeview with updated data including 'Edit' and 'Delete' buttons
        for i in range(len(self.video_data['ID'])):
            row_data = [self.video_data[key][i] for key in self.video_data.keys()]
            row_data.extend(['Edit', 'Delete'])  # Add 'Edit' and 'Delete' options to each row
            self.tree.insert("", "end", values=row_data)

    def load_data_from_file(self):
        try:
            with open(DATA_FILE, 'r') as file:
                lines = file.readlines()

            for key in self.video_data:
                self.video_data[key].clear()

            for line in lines:
                data = line.strip().split(',')
                if len(data) == len(self.video_data):
                    for key, value in zip(self.video_data.keys(), data):
                        self.video_data[key].append(value)

            self.populate_treeview_with_data()
        except FileNotFoundError:
            print("Video data file not found. Starting with empty data.")
        except Exception as e:
            print(f"Error loading data: {e}")

    def populate_treeview_with_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for i in range(len(self.video_data['ID'])):
            row_data = [self.video_data[key][i] for key in self.video_data.keys()]
            self.tree.insert("", "end", values=row_data + ['Edit', 'Delete'])

    def create_add_window(self):
        # Create a new window for adding video information
        add_window = tk.Toplevel(self.root)
        add_window.title("Add Video")

        # Labels and entry widgets for adding video information
        labels = ["ID:", "Name:", "Year:", "Director:", "Rating:", "Genre:", "Status:"]
        entry_widgets = []
        for row, label_text in enumerate(labels):
            label = tk.Label(add_window, text=label_text)
            label.grid(row=row, column=0, padx=5, pady=5, sticky='E')
            if label_text == "Status:":
                entry = tk.Spinbox(add_window, values=("Rented", "Available"), width=19)
            else:
                entry = tk.Entry(add_window)
            entry.grid(row=row, column=1, padx=5, pady=5, sticky='W')
            entry_widgets.append(entry)

        # Button to add video information in the new window
        add_video_button = tk.Button(add_window, text="Add Video", command=lambda: self.add_video_to_treeview(
            [entry.get() for entry in entry_widgets], add_window))
        add_video_button.grid(row=row + 1, columnspan=2, padx=5, pady=5)

    def confirm_rental(self, selected_item, customer_tree, rent_window):
        # Check if a customer is selected
        selected_customer = customer_tree.selection()
        if not selected_customer:
            messagebox.showerror("Error", "Please select a customer to rent the movie to.")
            return

        # Get the selected movie's title
        movie_title = self.tree.item(selected_item, 'values')[1]  # Assuming the movie title is in the second column

        # Get the selected customer's ID
        customer_id = customer_tree.item(selected_customer, 'values')[0]  # Assuming the customer ID is in the first column

        # Check if the customer has already rented the movie
        if self.is_movie_already_rented(customer_id, movie_title):
            messagebox.showerror("Error", "This movie is already rented by the selected customer.")
            return

        # Perform the movie rental operation, such as updating data, and save to file
        self.rent_movie_to_customer(customer_id, movie_title)

        # Close the rental popup
        rent_window.destroy()

    def is_movie_already_rented(self, customer_id, movie_title):
        # Check if the movie is already rented by the customer
        # Iterate through the customer data to find the customer by ID
        for i in range(len(self.customer_data['ID'])):
            if self.customer_data['ID'][i] == customer_id:
                # Check if the movie_title is already in the list of rented movies for the customer
                if movie_title in self.customer_data['Rented Movies'][i]:
                    return True  # Movie is already rented by the customer
        return False  # Movie is not rented by the customer

    def rent_movie_to_customer(self, customer_id, movie_title):
        # Find the index of the customer with the given customer_id
        customer_index = self.customer_data['ID'].index(customer_id)

        # Add the rented movie to the customer's list of rented movies
        self.customer_data['Rented Movies'][customer_index].append(movie_title)

        # Update the Treeview with the customer's rented movies
        self.tree.item(self.tree.selection(), values=self.customer_data['Rented Movies'][customer_index])

        # Save the updated customer data to the file
        self.save_data_to_file()

        # Show a confirmation message to the user
        messagebox.showinfo("Success", f"{movie_title} rented to customer {customer_id}.")

    def create_edit_window(self, item_data, selected_item):
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Customer")

        # Create labels and entry widgets for each column
        entry_widgets = {}
        for index, key in enumerate(self.customer_data.keys()):
            tk.Label(edit_window, text=key).grid(row=index, column=0)
            entry = tk.Entry(edit_window)
            entry.insert(0, item_data[index])
            entry.grid(row=index, column=1)
            entry_widgets[key] = entry

        # Button to save changes
        save_button = tk.Button(edit_window, text="Save Changes",
                                command=lambda: self.save_changes(selected_item, entry_widgets, edit_window))
        save_button.grid(row=len(self.customer_data.keys()), columnspan=2)

    def add_video_to_treeview(self, entries, add_window):
        # Add video information to the dictionary
        for i, key in enumerate(self.video_data):
            self.video_data[key].append(entries[i])

        # Insert data into the Treeview
        self.tree.insert("", "end", values=tuple(entries + ['Edit', 'Delete']))

        # Close the add window after adding video
        add_window.destroy()

        # Append new entry to video.txt in CSV format instead of writing the whole dictionary
        with open(DATA_FILE, 'a') as file:
            line = ','.join(entries)
            file.write(line + '\n')

    def on_treeview_click(self, event):
        region = self.tree.identify_region(event.x, event.y)
        if region == "cell":
            column = self.tree.identify_column(event.x)
            row_id = self.tree.identify_row(event.y)
            if self.tree.heading(column, 'text') == 'Edit':
                self.edit_video(row_id)
            elif self.tree.heading(column, 'text') == 'Delete':
                self.delete_video(row_id)

    def create_rent_popup(self):
        # This is the method to create the rental popup window
        rent_window = tk.Toplevel(self.root)
        rent_window.title("Rent Video")

        # Assume you have a list of customer names/IDs and video titles/IDs
        customer_names = self.get_customer_names()  # This should be a method returning customer names/IDs
        video_titles = self.get_video_titles()  # This should be a method returning video titles/IDs

        # Dropdown to select customer
        customer_var = tk.StringVar(rent_window)
        customer_dropdown = ttk.Combobox(rent_window, textvariable=customer_var, values=customer_names)
        customer_dropdown.grid(row=0, column=1)

        # Dropdown to select video
        video_var = tk.StringVar(rent_window)
        video_dropdown = ttk.Combobox(rent_window, textvariable=video_var, values=video_titles)
        video_dropdown.grid(row=1, column=1)

        # Add a 'Confirm' button that will call a method to process the rental
        confirm_button = tk.Button(rent_window, text="Confirm",
                                   command=lambda: self.process_rental(customer_var.get(), video_var.get(),
                                                                       rent_window))
        confirm_button.grid(row=2, columnspan=2)

    def delete_video(self, row_id):
        if messagebox.askyesno("Delete", "Are you sure you want to delete this video?"):
            # Get the ID of the video to be deleted
            video_id = self.tree.item(row_id, 'values')[0]
            # Remove the video from the data
            index = self.video_data['ID'].index(video_id)
            for key in self.video_data:
                self.video_data[key].pop(index)
            # Remove from Treeview and save
            self.tree.delete(row_id)
            self.save_data_to_file()

    def on_sort_selection(self, selection):
        # Get the current sorting order for the selected column, defaulting to ascending
        order = self.sort_order.get(selection, True)
        self.sort_treeview_data(selection, ascending=order)
        # Toggle the sorting order for the next sort
        self.sort_order[selection] = not order

    def sort_treeview_data(self, column, ascending=True):
        # Extract the data from the treeview
        data = [(self.tree.set(item, column), item) for item in self.tree.get_children('')]
        # Sort the data
        data.sort(reverse=not ascending)

        # Rearrange items in the treeview
        for index, (_, item) in enumerate(data):
            self.tree.move(item, '', index)

    def on_tree_click(self, event):
        item = self.tree.selection()[0]
        col = self.tree.identify_column(event.x)

        if col == '#8':  # Check if the clicked column is the 'Edit' column
            self.edit_row(item)
        elif col == '#9':  # Check if the clicked column is the 'Delete' column
            self.delete_row(item)

    def delete_row(self, item):
        # Find the index of the row in the dictionary
        index = self.tree.index(item)

        # Remove the row from the dictionary
        for key in self.video_data:
            self.video_data[key].pop(index)

        # Remove the row from the Treeview
        self.tree.delete(item)

    def search_video(self):
        # Get the video name to search for
        search_name = self.search_entry.get().lower()

        # Clear the Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Search for the video name in the stored data
        for i, name in enumerate(self.video_data['Name']):
            if search_name in name.lower():
                values = [self.video_data[key][i] for key in self.video_data.keys()] + ['Edit', 'Delete']
                self.tree.insert("", "end", values=values)

    def sort_treeview(self, event=None):
        column_to_sort = self.sort_column_var.get()
        current_items = [(self.tree.item(item, 'values'), item) for item in self.tree.get_children('')]
        current_items.sort(key=lambda x: x[0][list(self.video_data.keys()).index(column_to_sort)])

        for item in self.tree.get_children():
            self.tree.delete(item)

        for values, item in current_items:
            values_tuple = tuple(values)
            self.tree.insert("", "end", values=values_tuple + ('Edit', 'Delete'))

    def process_rental(self, customer_name, video_title, rent_window):
        # Validate selections
        if not customer_name or not video_title:
            messagebox.showerror("Error", "You must select both a customer and a video to rent.")
            return

        # Check if the video is already rented
        for video in self.video_data['Name']:
            if video_title == video and self.video_data['Status'][self.video_data['Name'].index(video)] == 'Rented':
                messagebox.showerror("Error", "This video is already rented.")
                return

        # Update the video status to 'Rented'
        try:
            video_index = self.video_data['Name'].index(video_title)
            self.video_data['Status'][video_index] = 'Rented'
            self.update_treeview()  # Assuming this method refreshes the Treeview with the current data
            self.save_data_to_file()  # Assuming this method saves the current state of video_data to a file

            # Log the rental in a simplistic rental log (you'd likely have a more complex system in a real application)
            rental_log_entry = f"Customer: {customer_name}, Video: {video_title}, Status: Rented\n"
            with open('rental_log.txt', 'a') as rental_log:  # Append to a rental log file
                rental_log.write(rental_log_entry)

            messagebox.showinfo("Success", f"The video '{video_title}' has been rented to '{customer_name}'.")
        except ValueError as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", "An unexpected error occurred while processing the rental.")
        finally:
            rent_window.destroy()  # Close the rent window regardless of the outcome

    def save_changes(self, item, entry_widgets, edit_window):
        # Check if all elements in entry_widgets are Entry widgets
        if not all(isinstance(entry, tk.Entry) for entry in entry_widgets.values()):
            print("Not all elements in entry_widgets are Entry widgets.")
            return

        # Get the updated values from entry widgets
        updated_values = [entry.get() for entry in entry_widgets.values()]

        # Update the Treeview with the new values
        self.tree.item(item, values=updated_values + ['Edit', 'Delete'])

        # Update the dictionary with the new values
        row_index = self.tree.index(item)
        for col, value in zip(self.video_data.keys(), updated_values):
            self.video_data[col][row_index] = value

        # Save the changes to the text file
        self.save_data_to_file()

        # Close the edit window
        edit_window.destroy()

    def save_data_to_file(self):
        with open(DATA_FILE, 'w') as file:
            for i in range(len(self.video_data['ID'])):
                line = ','.join([str(self.video_data[key][i]) for key in self.video_data.keys()])
                file.write(line + '\n')

    def edit_video(self, row_id):
        # Fetch the item's data
        item = self.tree.item(row_id)['values']
        # Create a new Toplevel window
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Video")

        # Create Entry widgets for each column, pre-fill them with the item's data
        entries = {}
        for index, key in enumerate(self.video_data.keys()):
            tk.Label(edit_window, text=key).grid(row=index, column=0)
            entry = tk.Entry(edit_window)
            entry.grid(row=index, column=1)
            entry.insert(0, item[index])
            entries[key] = entry

        # Button to save changes
        save_button = tk.Button(edit_window, text="Save Changes",
                                command=lambda: self.save_changes(row_id, entries, edit_window))
        save_button.grid(row=len(self.video_data.keys()), columnspan=2)

    def edit_selected_item(self):
        selected_item = self.tree.selection()
        if selected_item:
            item_data = self.tree.item(selected_item, 'values')
            # Assuming a method to create an edit window similar to the add window but with pre-filled data
            self.create_edit_window(item_data, selected_item)


class CustomerInfoApp:
    def __init__(self, root):
        self.root = root
        self.customer_data = {'ID': [], 'First Name': [], 'Last Name': [], 'Address': [],
                              'Phone Number': [], 'Email Address': []}
        self.sort_column_var = tk.StringVar()
        self.initialize_ui()
        self.read_customer_data_from_file()  # Load customer data from file when the app starts

    def create_add_window(self):
        # Create a new window for adding customer information
        add_window = tk.Toplevel(self.root)
        add_window.title("Add Customer")

        # Labels and entry widgets for adding customer information
        labels = ['ID:', 'First Name:', 'Last Name:', 'Address:', 'Phone Number:', 'Email Address:']
        entry_widgets = []
        for row, label_text in enumerate(labels):
            label = tk.Label(add_window, text=label_text)
            label.grid(row=row, column=0, padx=5, pady=5, sticky='W')
            entry = tk.Entry(add_window)
            entry.grid(row=row, column=1, padx=5, pady=5, sticky='EW')
            entry_widgets.append(entry)

        # Button to add customer information in the new window
        add_customer_button = tk.Button(add_window, text="Add Customer", command=lambda: self.add_customer_to_treeview(
            [entry.get() for entry in entry_widgets], add_window)
                                        )
        add_customer_button.grid(row=row + 1, columnspan=2, padx=5, pady=5)

    def save_customer_data_to_file(self):
        with open(CUSTOMER_DATA_FILE, 'w') as file:
            for i in range(len(self.customer_data['ID'])):
                customer_info = [self.customer_data[key][i] for key in self.customer_data.keys()]
                file.write(','.join(customer_info) + '\n')

    def read_customer_data_from_file(self):
        try:
            with open('customer.txt', 'r') as file:
                lines = file.readlines()
                for line in lines:
                    data = line.strip().split(',')
                    if len(data) == len(self.customer_data):
                        for key, value in zip(self.customer_data.keys(), data):
                            self.customer_data[key].append(value)
                        self.tree.insert("", "end", values=tuple(data + ['Edit', 'Delete']))
        except FileNotFoundError:
            print("File 'customer_data.txt' not found")

    def add_customer_to_treeview(self, entries, add_window):
        # Add customer information to the dictionary
        self.customer_data['ID'].append(entries[0])
        self.customer_data['First Name'].append(entries[1])
        self.customer_data['Last Name'].append(entries[2])
        self.customer_data['Address'].append(entries[3])
        self.customer_data['Phone Number'].append(entries[4])
        self.customer_data['Email Address'].append(entries[5])

        # Insert data into the Treeview
        self.tree.insert("", "end", values=tuple(entries + ['Edit', 'Delete']))

        # Close the add window after adding customer
        add_window.destroy()

        # Save the updated data to the file
        self.save_customer_data_to_file()

    def initialize_ui(self):
        self.open_add_window_button = tk.Button(self.root, text="Add New Customer", command=self.create_add_window)
        self.open_add_window_button.grid(row=2, column=8, columnspan=2, padx=10, pady=5)

        self.manage_customer_label = tk.Label(self.root, text="Manage Customer", font=("Times New Roman", 16, "bold"))
        self.manage_customer_label.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky='W')  # Align to the left

        self.sort_label = tk.Label(self.root, text="Sort:")
        self.sort_label.grid(row=4, column=0, padx=5, pady=5, sticky='E')  # Align to the right

        self.search_label = tk.Label(self.root, text="Search by Name:")
        self.search_label.grid(row=4, column=6, padx=5, pady=5, sticky='EW')  # Align to the right

        self.search_entry = tk.Entry(self.root)
        self.search_entry.grid(row=4, column=7, padx=5, pady=5, sticky='EW')  # Default alignment to the left

        self.search_button = tk.Button(self.root, text="Search", command=self.search_customer)
        self.search_button.grid(row=4, column=8, padx=5, pady=5, sticky='EW')  # Default alignment to the left

        self.tree = ttk.Treeview(self.root, columns=list(self.customer_data.keys()) + ['Edit', 'Delete'],
                                 show='headings')
        for col in self.customer_data.keys():
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)

        self.tree.heading('Edit', text='Edit')
        self.tree.column('Edit', width=80)

        self.tree.heading('Delete', text='Delete')
        self.tree.column('Delete', width=80)

        self.sort_combobox = ttk.Combobox(self.root, textvariable=self.sort_column_var,
                                          values=list(self.customer_data.keys()))
        self.sort_combobox.grid(row=4, column=1, padx=5, pady=5)
        self.sort_combobox.bind("<<ComboboxSelected>>", self.sort_treeview)

        self.pack_ui_elements()
        self.tree.bind("<ButtonRelease-1>", self.on_tree_click)

        separator = ttk.Separator(self.root, orient='horizontal')
        separator.grid(row=3, column=0, columnspan=9, sticky="ew", pady=5)

    def pack_ui_elements(self):
        # Pack labels, entry widgets, and buttons
        ui_elements = [
            (self.manage_customer_label, 2, 0),
            (self.sort_label, 4, 0),
            (self.search_label, 4, 6),
            (self.search_entry, 4, 7),
            (self.search_button, 4, 8)
        ]

        for element, row, col in ui_elements:
            element.grid(row=row, column=col, padx=1, pady=5)

        self.tree.grid(row=6, column=0, columnspan=9, padx=5, pady=5)

    def on_tree_click(self, event):
        item = self.tree.selection()[0]
        col = self.tree.identify_column(event.x)

        if col == '#7':  # Check if the clicked column is the 'Edit' column
            self.edit_row(item)
        elif col == '#8':  # Check if the clicked column is the 'Delete' column
            self.delete_row(item)

    def edit_row(self, item):
        # Implementation for editing a row
        # Get the values of the selected row
        values = self.tree.item(item, 'values')

        # Create a new Toplevel window for editing
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Row")

        entry_widgets = []
        # Create labels and entry widgets for each column
        for row, (col, value) in enumerate(zip(self.customer_data.keys(), values[:-2])):
            label = tk.Label(edit_window, text=f"{col}:")
            label.grid(row=row, column=0, padx=10, pady=5)

            entry = tk.Entry(edit_window)
            entry.insert(0, value)
            entry.grid(row=row, column=1, padx=10, pady=5)
            entry_widgets.append(entry)

        # Create a button to save changes
        save_button = tk.Button(edit_window, text="Save Changes",
                                command=lambda: self.save_changes(item, entry_widgets, edit_window))
        save_button.grid(row=len(self.customer_data.keys()), columnspan=2, pady=10)

    def delete_row(self, item):

        # Find the index of the row in the dictionary
        index = self.tree.index(item)

        # Remove the row from the dictionary
        for key in self.customer_data:
            self.customer_data[key].pop(index)

        # Remove the row from the Treeview
        self.tree.delete(item)

    def save_changes(self, item, entry_widgets, edit_window):

        # Get the updated values from entry widgets
        updated_values = [entry.get() for entry in entry_widgets]

        # Update the Treeview with the new values
        self.tree.item(item, values=updated_values + ['Edit', 'Delete'])

        # Update the dictionary with the new values
        row_index = self.tree.index(item)
        for col, value in zip(self.customer_data.keys(), updated_values):
            self.customer_data[col][row_index] = value

        # Close the edit window
        edit_window.destroy()

    def search_customer(self):

        # Get the video name to search for
        search_name = self.search_entry.get().lower()

        # Clear the Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Search for the video name in the stored data
        for i, name in enumerate(self.customer_data['First Name']):
            if search_name in name.lower():
                values = [self.customer_data[key][i] for key in self.customer_data.keys()] + ['Edit', 'Delete']
                self.tree.insert("", "end", values=values)

    def sort_treeview(self, event=None):
        column_to_sort = self.sort_column_var.get()
        current_items = [(self.tree.item(item, 'values'), item) for item in self.tree.get_children('')]
        current_items.sort(key=lambda x: x[0][list(self.customer_data.keys()).index(column_to_sort)])

        for item in self.tree.get_children():
            self.tree.delete(item)

        for values, item in current_items:
            values_tuple = tuple(values)
            self.tree.insert("", "end", values=values_tuple + ('Edit', 'Delete'))


if __name__ == "__main__":
    app = TabbedApp()
    app.add_tab(VideoInfoApp, "Manage Video")
    app.add_tab(CustomerInfoApp, "Manage Customer")
    app.run()
