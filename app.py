import os
from models import (Base, session, Product, engine)
import csv
import datetime
import time



def clean_date(date_str):
    split_date = date_str.split('/')
    try:
        month = int(split_date[0])
        day = int(split_date[1])
        year = int(split_date[2])
        return_date = datetime.date(year, month, day)
    except ValueError:
        print(f"Oops try again. Enter a date in format: mm/dd/yyyy")
        input('''
        \n****** DATE ERROR *****
        \rThe date format should include a valid Month Day, Year
        \rPress ENTER to try again.
        \r********************************************************
        ''')
        return
    else:
        return return_date


def clean_price(price_str):
    split_price = price_str.split('$')
    try:
        price_float = float(split_price[1])
    except ValueError:
        input('''
        \n****** PRICE ERROR *****
        \rThe price format should be a number without currency symbol
        \rEx 10.99
        \rPress ENTER to try again.
        \r********************************************************
        ''')
    else:
        return int(price_float * 100)


def clean_id(id_str, options):
    try:
        product_id = int(id_str)
    except ValueError:
        input('''
        \n****** ID ERROR *****
        \rThe ID format should be a number.
        \rPress ENTER to try again.
        \r********************************************************
        ''')
        return
    else:
        if product_id in options:
            return product_id
        else:
            input(f'''
                    \n****** ID ERROR *****
                    \rOptions:  {options}
                    \rPress ENTER to try again.
                    \r********************************************************
                    ''')
            return


def add_csv():
    with open('inventory.csv') as csvfile:
        data = csv.reader(csvfile)
        next(data)  # <<< skip header row
        for row in data:
            product_in_db = session.query(Product).filter(Product.product_name == row[0]).one_or_none()
            if product_in_db is None:
                product_name = row[0]
                product_price = clean_price(row[1])
                product_quantity = row[2]
                date_updated = clean_date(row[3])
                new_product = Product(product_name=product_name, product_price=product_price,
                                      product_quantity=product_quantity, date_updated=date_updated)
                session.add(new_product)
        session.commit()


def backup_csv():
    backup_csv_filename = 'backup.csv'
    if not os.path.exists('backup.csv'):
        # print("File exists. Creating backup copy")
        # date_append = datetime.date.today()
        # os.rename('backup.csv', f'{date_append}_backup.csv')
        #header = session.query(Product)
        print(Product.product_id)
        with open(backup_csv_filename, 'w', newline='') as csvfile:
            backup_write = csv.writer(csvfile, delimiter=',')
            header_row = session.query(Product)
            backup_write.writerow(header_row.product_id, header_row.product_name, header_row.product_quantity, header_row.product_price)
            for product in session.query(Product):
                pass

        #     print(product.product_id)
    else:
        print("file exists")
        # print(datetime.date.today())
        # for product in session.query(Product):
        #     print(product.product_id)



def menu():
    while True:
        print('''
        \nINVENTORY MANAGEMENT
        \rV) View a single product's inventory
        \rA) Add a new product to the database
        \rB) Make a backup of the entire inventory
        \rQ) Quit
        ''')
        menu_option = input('What would you like to do? ').upper()
        if menu_option in ['V', 'A', 'B', 'Q']:
            return menu_option
        else:
            input('Choose one of the options above. Press Enter to try again. ')


def display_product_by_id(product_id):
    the_product = session.query(Product).filter(Product.product_id == product_id).first()
    return the_product


def add_product_to_database(product_name, product_price, product_quantity, product_date):
    print(product_name, product_quantity, product_price, product_date)
    new_product = Product(product_name=product_name, product_price=product_price, product_quantity=product_quantity,
                          date_updated=product_date)
    session.add(new_product)
    session.commit()
    print(f"Product added!")
    time.sleep(1.5)


def app():
    app_running = True
    while app_running:
        menu_option = menu()
        if menu_option == 'V':
            id_options = []
            for product in session.query(Product):
                id_options.append(product.product_id)
            id_error = True
            while id_error:
                id_choice = input(f'''
                                \nID Options:  {id_options}
                                \rBook ID:  
                                ''')
                id_choice = clean_id(id_choice, id_options)
                if type(id_choice) == int:
                    id_error = False
                    the_product = display_product_by_id(id_choice)
                    print(f'''
                    \nProduct ID:  {the_product.product_id}
                    \rProduct name:  {the_product.product_name}
                    \rQuantity on hand:  {the_product.product_quantity}
                    \rLast update:  {the_product.date_updated}
                        ''')
        elif menu_option == 'A':
            name_error = True
            while name_error:
                name = input('Product name:  ')
                name = name.lstrip(' ')
                if name.isascii():
                    name_error = False
                else:
                    print("OOPS")

            price_error = True
            while price_error:
                price = input('Price (Ex: 9.99): ')
                price = clean_price('$' + price)
                if type(price) == int:
                    price_error = False

            quantity_error = True
            while quantity_error:
                try:
                    quantity_on_hand = int(input('Quantity:  '))
                    if type(quantity_on_hand) == int:
                        quantity_error = False
                except ValueError:
                    print(f"Oops try again. Enter a number only")

            # date_error = True
            # while date_error:
            #     date_updated = input('Product date added: (Ex: 01/31/2023): ')
            #     date_updated = clean_date(date_updated)
            #     if type(date_updated) == datetime.date:
            #         date_error = False

            date_updated = datetime.datetime.now()

            add_product_to_database(name, price, quantity_on_hand, date_updated)
        elif menu_option == 'B':
            pass
        else:
            print(f"Quitting application...")
            time.sleep(1.5)
            app_running = False


if __name__ == '__main__':
    Base.metadata.create_all(engine)
    #add_csv()
    #app()
    backup_csv()
