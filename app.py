import os
import models
from models import (Base, session, Product, engine, update)
import csv
import datetime
import time
from decimal import Decimal


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
        price_float = Decimal(split_price[1])
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
        id_to_int = int(id_str)
    except ValueError:
        input('''
        \n****** ID ERROR *****
        \rThe ID format should be a number.
        \rPress ENTER to try again.
        \r********************************************************
        ''')
        return
    else:
        if id_to_int in options:
            return id_to_int
        else:
            input(f'''
                    \n****** ID ERROR *****
                    \rOptions:  {options}
                    \rPress ENTER to try again.
                    \r********************************************************
                    ''')
            return


def add_csv_dict():
    csv_file_to_import = 'inventory.csv'
    if os.path.isfile(csv_file_to_import):
        Base.metadata.create_all(engine, checkfirst=True)
        with open(csv_file_to_import, newline="") as csvfile:
            data = csv.DictReader(csvfile)
            for row in data:
                product_name = row['product_name']
                product_price = clean_price(row['product_price'])
                product_quantity = row['product_quantity']
                date_updated = clean_date(row['date_updated'])
                product = session.query(Product).filter_by(product_name=product_name).first()
                if product:
                    if date_updated > product.date_updated:
                        product.product_price = product_price
                        product.product_quantity = product_quantity
                        product.date_updated = date_updated
                else:
                    product = Product(product_name=product_name, product_price=product_price,
                                      product_quantity=product_quantity, date_updated=date_updated)
                    session.add(product)
            session.commit()
        return True
    else:
        print(f"CSV to import not found.")
        print(f"Quitting application...")
        time.sleep(1.5)
        return False


def backup_csv_dict():
    backup_csv_filename = 'backup.csv'
    products = session.query(Product).all()
    file_exists_error = True
    while file_exists_error:
        if os.path.exists(backup_csv_filename):
            print("File exists! Renaming existing file by appending '_old'")
            os.replace(backup_csv_filename, 'backup_old.csv')
            continue
        else:
            print("Writing new backup.csv")
            with open(backup_csv_filename, 'w', newline='') as csvfile:
                fieldnames = ['product_name', 'product_price', 'product_quantity', 'date_updated']
                csvwriter = csv.DictWriter(csvfile, fieldnames=fieldnames)
                csvwriter.writeheader()
                for product in products:
                    csv_price = '$' + str(format(product.product_price / 100, '.2f'))
                    csv_date = product.date_updated.strftime("%m/").lstrip("0") + \
                               product.date_updated.strftime("%d/").lstrip("0") + \
                               product.date_updated.strftime("%Y")
                    csvwriter.writerow({'product_name': product.product_name,
                                        'product_price': csv_price,
                                        'product_quantity': product.product_quantity,
                                        'date_updated': csv_date
                                        })
            file_exists_error = False
            print("'backup.csv' has been saved!")
            time.sleep(1.5)


def display_product_by_id(id):
    the_product = session.query(Product).filter(Product.id == id).first()
    return the_product


def add_product_to_database(productname, productprice, productquantity, productdate):
    print(productname, productprice, productquantity, productdate)
    if session.query(Product).filter(Product.product_name == productname).first():
        print("record exists")
        stmt = (update(Product).where(Product.product_name == productname).values(product_price=productprice,
                                                                                  product_quantity=productquantity,
                                                                                  date_updated=productdate))
        session.execute(stmt)
        session.commit()
        print(f"Product updated!")
        time.sleep(1.5)
    else:
        new_product = Product(product_name=productname, product_price=productprice, product_quantity=productquantity,
                              date_updated=productdate)
        session.add(new_product)
        session.commit()
        print(f"Product added!")
        time.sleep(1.5)


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


def app():
    app_running = True
    while app_running:
        menu_option = menu()
        if menu_option == 'V':
            id_options = []
            for product in session.query(Product):
                id_options.append(product.id)
            id_error = True
            while id_error:
                print(f"ID Options:  {id_options}")
                id_choice = input(f"Product ID:  ")
                id_choice = clean_id(id_choice, id_options)
                if type(id_choice) == int:
                    id_error = False
                    the_product = display_product_by_id(id_choice)
                    print(f'''
                    \nProduct ID:  {the_product.id}
                    \rProduct name:  {the_product.product_name}
                    \rPrice:  $ {the_product.product_price / 100}
                    \rQuantity on hand:  {the_product.product_quantity}
                    \rLast update:  {the_product.date_updated}
                        ''')
        elif menu_option == 'A':
            name_error = True
            while name_error:
                name = input('Product name:  ')
                name = name.lstrip(' ')
                if name.isascii() and not name.isspace() and not name == '':
                    name_error = False
                else:
                    print("You did not enter a product name. Try again. \n")

            price_error = True
            while price_error:
                try:
                    price = float(input('Price (Ex: 9.99): '))
                    if price < 0:
                        print(f"Enter a number greater than or equal to 0 (zero)")
                    else:
                        price = str(price)
                        price = clean_price('$' + price)
                        price_error = False
                except ValueError:
                    print("Enter a valid number without currency symbol (e.g. $)")

            quantity_error = True
            while quantity_error:
                try:
                    quantity_on_hand = int(input('Quantity:  '))
                    if type(quantity_on_hand) == int:
                        quantity_error = False
                except ValueError:
                    print(f"Oops try again. Enter a number only")

            date_updated = datetime.date.today()

            add_product_to_database(name, price, quantity_on_hand, date_updated)
        elif menu_option == 'B':
            # backup_csv()
            backup_csv_dict()
        else:
            print(f"Quitting application...")
            time.sleep(1.5)
            app_running = False


if __name__ == '__main__':
    if add_csv_dict():
        app()
