import matplotlib
matplotlib.use('TkAgg')
from tkinter import DoubleVar, StringVar, IntVar, ttk, Tk, BOTH, RIGHT, RAISED, LEFT, X, Listbox, Message, messagebox, simpledialog, END
from tkinter.ttk import Frame, Radiobutton, Button, Style, Label, Entry, Treeview
import tkinter as tk
import dbmanager
import configreader
import chartmaker
import serialManager
from functools import partial

class WarehouseFrame(Frame):
    def __init__(self):
        super().__init__()
        #read the configs in the 'config' file. File must be at the same level as app folder
        self.config = configreader.ConfigReader()
        self.config.readconfig()

        #gets the names designated for each serial
        self.names = [self.config.serial1['name'].strip(),
                    self.config.serial2['name'].strip(),
                    self.config.serial3['name'].strip(),
                ]

        #init serial manager -- serial manager manages all process involving serial port. Read and write to be exact
        self.initSerialPort()

        #init db manager -- db manager manages all process involving database. SELECT, INSERT UPDATE and DELETE
        self._initdb_()

        #init user interface
        self.initUI()

        #this is a flag that indicates that the system is waiting for a response after the scan button is pressed
        self._isWaiting = False;

    def initSerialPort(self):
        self._serialMan = serialManager.SerialManager(self.config, self.cbScan, self.cbCheckout)

    def _initdb_(self):
        self._dbman = dbmanager.DbManager(self.config.username, self.config.pw
                ,self.config.host ,self.config.db)
        self._dbman.connect()
    def initUI(self):
        self.style = Style()
        self.style.theme_use("clam")

        self.searchframe = Frame(self, relief=RAISED, borderwidth=1)
        self.searchframe.pack(fill=BOTH, expand=True)
        self.tableframe = Frame(self, relief=RAISED, borderwidth=1)
        self.tableframe.pack(fill=BOTH, expand=True)

        self.master.title("Item Manager")
        self.pack(fill=BOTH, expand=1)

        #create tree view -- this is the table that will hold the data after query
        self.CreateTV()

        #this loads the data into the treeview
        self.LoadTable()

        #button for adding new items in the items table, calls CreateWindow function when clicked
        createButton = Button(self, text="Add Item", command=self.CreateWindow)
        createButton.pack(side=LEFT, padx=5, pady=5)

        #button for deleting items from the items table, call DeleteWindow function when clicked
        deleteButton = Button(self, text="Delete Item", command=self.DeleteWindow)
        deleteButton.pack(side=LEFT, padx=5, pady=5)

        #button for scanning, calls Scan function when clicked
        scanButton = Button(self, text="Scan", command=self.Scan)
        scanButton.pack(side=LEFT, padx=5, pady=5)

        #button to initialize the readers based on the config file, calls SerialManagers initializesystem function
        startButton = Button(self, text="Start", command=self._serialMan.initializeSystem)
        startButton.pack(side=LEFT, padx=5, pady=5)

        #button to add product in the products table, calls CreateProduct function
        prodButton = Button(self, text="Add Product", command=self.CreateProduct)
        prodButton.pack(side=LEFT, padx=5, pady=5)

        #searching
        self.CreateSearchButton();

        quitButton = Button(self, text="Quit",
                command=self.quit)
        quitButton.pack(side=RIGHT, padx = 5, pady = 5)

        #this opens the checkout window
        self.checkoutWindow()

    def checkoutWindow(self):
        self.coWin = tk.Toplevel()
        self.coWin.title("Checkout")
        self.items = Label(self.coWin, text="Waiting...")
        self.items.grid()
        self.collections = []

        self.cobutton = Button(self.coWin, text="Checkout", command=self.Checkout)
        self.cobutton.grid(row=2, column=1)


    def Checkout(self):
        #do aggregation here
        query = "SELECT Product, count(Product) as Quantity from items where EPC in ({}) group by Product".format(','\
                .join("'{}'".format(e) for e in self.collections))
        result = self._dbman.executeCustomQuery(query)
        text = []
        if result[0] > 0:
            for i in result[1]:
                text.append('{} - x {}'.format(i['Product'], i['Quantity']))

        res = messagebox.askyesno('Checkout Summary!', 'The following items will be checked out:\
    \n {} \nContinue?'.format('\n'.join(text)))
        if res:
            query = "DELETE from items where EPC in ({})".format(','\
                .join("'{}'".format(e) for e in self.collections))
            result = self._dbman.executeCustomQuery(query)
            if result[0] > 0:
                messagebox.showinfo('Checkout Notice', "Checkout Success! Database updated")
                self.collections = []
                self.items['text'] = "Nothing to checkout."
                self.LoadTable()
            else:
                messagebox.showinfo('Checkout Notice', "Something went wrong with the checkout")

    def cbCheckout(self, tags):
        print('checkout cb')
        if(len(tags) > 0):
            #query product
            #update text
            epcs = []
            for c in tags:
                #formats the epc in HEX format with zero padding 0xa -> 0A, 0xFF -> FF then concatenate
                # 0xa0xff -> 0AFF
                epc = ''.join('{:02x}'.format(t) for t in c[1]).strip().upper()
                if epc not in self.collections and epc not in epcs:
                        epcs.append(epc)

            if(len(epcs) > 0):
                query = "SELECT * from items where EPC in ({})".format(','.join("'{}'".format(e) for e in epcs))
                result = self._dbman.executeCustomQuery(query)

                if result[0] > 0:
                    text = []
                    for i in result[1]:
                        text.append('Product:{} '.format(i['Product']))
                    status = self.items['text']
                    self.items['text'] = '{}\n{}'.format(status, '\n'.join(text))
                else:
                    messagebox.showinfo('Checkout Notice', "Item not registered")


                self.collections.extend(epcs)

    def CreateProduct(self, event=None):
        self.newwin = tk.Toplevel()
        self.newwin.title("Add Product")
        self.namelbl = Label(self.newwin, text="Name", width=6)
        self.namelbl.grid(row=0,column=0)
        self.prodent = Entry(self.newwin,)
        self.prodent.grid(row=0, column=1)

        self.addProdbutton = Button(self.newwin, text="Add", command=self.CreateProd)
        self.addProdbutton.grid(row=2, column=1)

    def CreateProd(self, event=None):
        result = 0;

        e = dbmanager.ProductDict()
        e['name'] = self.prodent.get()
        result = self._dbman.AddToTable('products', e)

        if(-1 == result):
            messagebox.showinfo('Create Notice', "Create one or more items failed! Name must be unique!")
        else:
            messagebox.showinfo('Create Notice', "Create success!")
            self.newwin.destroy()
            self.LoadTable()

    def CreateWindow(self, event=None):
        self.newwin = tk.Toplevel()
        self.newwin.title("add item")
        self.epclbl = Label(self.newwin, text="EPC", width=6)
        self.epclbl.grid(row=1, column=0)
        self.epcbox_value = StringVar()
        self.epccombo= ttk.Combobox(self.newwin, textvariable=self.epcbox_value, state='readonly')
        self.epccombo.grid(row=1,column=1)
        l = self._createlist("select {} from {}".format('epc','epc'))
        if(len(l) > 0):
            self.epccombo['values'] = self._createlist("select {} from {}".format('epc','epc'))
            self.epccombo.current(0)
        else:
            messagebox.showinfo('Create Notice', "No more available EPC to assign")


        self.prodlbl = Label(self.newwin, text="Product", width=6)
        self.prodlbl.grid(row=2, column=0)
        self.prodbox_value = StringVar()
        self.prodcombo= ttk.Combobox(self.newwin, textvariable=self.prodbox_value, state='readonly')
        self.prodcombo.grid(row=2,column=1)
        self.prodcombo['values'] = self._createlist("select {} from {}".format('name','products'))
        self.prodcombo.current(0)

        self.addbutton = Button(self.newwin, text="Add", command=self.Create)
        self.addbutton.grid(row=5, column=1)



    def cbScan(self, tags):
        if self._isWaiting:
            self._isWaiting = False
            confirmed_tags = []
            queried = []
            print('tags count: ',len(tags))
            #checks if there are scanned tags
            if len(tags) > 0:
                for tag in tags:
                    epc = ''.join('{:02x}'.format(t) for t in tag[1]).strip().upper()
                    if epc != '':
                        query = "SELECT Location, Product from items where epc='{}'".format(epc)
                    if epc not in queried:
                        result = self._dbman.executeCustomQuery(query)
                        if(0 < result[0]):
                            new_loc = self.names[tag[0] - 1]
                            old_loc = result[1][0]['Location']
                            product = result[1][0]['Product'].strip()

                            #check if the tag has already been registered by checking if the location is empty
                            if old_loc == None:
                                #update db
                                row = simpledialog.askstring('Input Row', '{}: Enter row for: {}\nEPC:{}'.format(new_loc, product, epc))
                                query = "UPDATE items SET location='{}' WHERE epc='{}'".format('{} : {}'.format(new_loc, row), epc)

                                result = self._dbman.executeCustomQuery(query)
                                if 0 < result[0]:
                                    confirmed_tags.append((epc, product, new_loc))

                            #check if the tag has been registered before but was relocated to other shelf
                            elif old_loc.split(':')[0].strip() != new_loc:
                                #raise error and update db
                                res = messagebox.askyesno('Notice!', 'Product with EPC:{} is originally from {} but was found in {}.\
                        \nUpdate?'.format(epc, old_loc.strip(), new_loc))
                                if res:
                                    self.UpdateLoc(epc, new_loc)

                        #this adds new tags that are not yet registered  in the EPC table,
                        else:
                            #this query ignores if the EPC already exist in the DB. Inserts otherwise
                            query = "INSERT IGNORE INTO EPC(epc) values('{}')".format(epc)
                            result =self._dbman.executeCustomQuery(query)
                            if 0 < result[0]:
                                messagebox.showinfo('Notice', "Product with EPC={} is not preregistered! Adding in EPC table".format(epc))

                            else:
                                messagebox.showinfo('Notice', "Cannot ADD EPC='{}' to table already exists".format(epc))

                    queried.append(epc)





            if len(confirmed_tags) > 0:
                messagebox.showinfo('New Items Registered',
                            'The following items have been added:\n {}'.format(
                                '\n'.join('EPC: {} Product: {} in {}'.format(epc, product, loc) for epc,product,loc in confirmed_tags)
                                )
                        )
            #query all
            query = "SELECT * from items where location !=''"
            result = self._dbman.executeCustomQuery(query)
            if(0 < result[0]):

                #check for missing items:
                for p in result[1]:
                    print(p['epc'])
                    print(queried)
                    if p['epc'] not in queried:
                        messagebox.showinfo('Notice', "Product {} with EPC: {} missing from {}!".format(p['Product'], p['epc'], p['location']))

            self.LoadTable()

    def Scan(self):
        self._serialMan.scan(self.cbScan)
        self._isWaiting = True;

    def UpdateLoc(self, epc, loc):
        row = simpledialog.askstring('Input Row', '{}: Enter row for: {}\nEPC:{}'.format(new_loc, product, epc))
        query = "UPDATE items SET location='{}' WHERE epc='{}'".format('{} : {}'.format(new_loc, row), epc)

        result = self._dbman.executeCustomQuery(query)
        if 0 < result[0]:
            messagebox.showinfo('Success', 'Location update for product with EPC:{} Success!'.format(epc))
        else:
            messagebox.showinfo('Fail', 'Location update for product with EPC:{} Failed!'.format(epc))





    def Search(self,event=None):
        #searches the items table based on the name of the product
        alllist = self._dbman.getAllWhere("product like '%{}%'".format(self.searchtext.get()))

        if(0 < alllist[0]):
            for i in self.tv.get_children():
                self.tv.delete(i)

            for item in alllist[1]:
                self.tv.insert('', 'end',  values=(item['EPC'], item['Product'], item['Location'], item['Quantity']))
        else:
            messagebox.showinfo('Search','{} not found in {}!'.format(self.searchtext.get(), self.box.get()))

    def CreateSearchButton(self):
        self.searchlbl = Label(self.searchframe, text="Search", width=6)
        self.searchlbl.pack(side=LEFT, padx=5, pady=5)
        self.searchtext = Entry(self.searchframe)
        self.searchtext.pack(side=LEFT, padx=5, expand=True)
        self.searchButton = Button(self.searchframe, text="Search", command=self.Search)
        self.searchButton.pack(side=RIGHT, padx=5)




    def _createlist(self, srcquery):
        result = self._dbman.executeCustomQuery(srcquery)
        objlist = []
        if(0 < result[0]):
            for item in result[1]:
                for key in item.keys():
                    objlist.append(item[key])
        return objlist

    def DeleteWindow(self, event=None):
        self.newwin = tk.Toplevel()
        self.newwin.title("Delete Item")
        self.lbldestroyfrom = Label(self.newwin, text='EPC', width=6)
        self.lbldestroyfrom.grid(row=0,column=0)
        self.epcbox_value = StringVar()
        self.epccombo= ttk.Combobox(self.newwin, textvariable=self.epcbox_value, state='readonly')
        self.epccombo.grid(row=0,column=1)
        self.epccombo['values'] = self._createlist("select {} from {} order by product".format('epc','items'))
        self.epccombo.current(0)

        self.destroyButton = Button(self.newwin, text="Delete", command=self.Delete)
        self.destroyButton.grid(row=1, column=1)

    def Delete(self, event=None):
        result = 0;

        if(-1 != self.epccombo.current()):
            result = self._dbman.deleteFromTable('items','epc', self.epccombo.get())
        else:
            result = (1,())

        if(1 != result[0]):
            messagebox.showinfo('Destroy Notice', "Deleting {} failed!\r\n {}".format(self.idcombo.get(), result[1]))
        else:
            messagebox.showinfo('Destroy Notice', "Delete success!")
            self.newwin.destroy()
            self.LoadTable()

    def Create(self, event=None):
        result = 0;

        e = dbmanager.ItemDict()
        e['epc'] = self.epccombo.get()
        e['product'] = self.prodcombo.get()
        result = self._dbman.AddToTable('items', e)

        if(-1 == result):
            messagebox.showinfo('Create Notice', "Create one or more items failed!")
        else:
            query = "DELETE FROM epc where epc='{}'".format(self.epccombo.get())
            result = self._dbman.executeCustomQuery(query)
            if 0 > result[0]:
                messagebox.showinfo('Notice', "Something happended EPC='{}'".format(epc))
            messagebox.showinfo('Create Notice', "Create success!")
            self.newwin.destroy()
            self.LoadTable()

    def CreateTV(self):
        self.tv = Treeview(self.tableframe)
        self.tv['show'] = 'headings'
        self.tv['columns'] = ( 'Product','Location', 'Quantity')
        self.tv.heading('Product', text='Product')
        self.tv.column('Product', width=100)
        self.tv.heading('Location', text='Location')
        self.tv.column('Location', width=100)
        self.tv.heading('Quantity', text='Quantity')
        self.tv.column('Quantity',  width=100)
        self.tv.pack(fill=X, side='left', expand=True)
        vsb = ttk.Scrollbar(self.tableframe, orient="vertical", command=self.tv.yview)
        vsb.pack(side='right', fill='y')

    def LoadTable(self):
        alllist = self._dbman.executeCustomQuery('call get_summary')[1]

        for i in self.tv.get_children():
            self.tv.delete(i)

        for item in reversed(alllist):
            if item['Location'] != None:
                self.tv.insert('', 'end',  values=(item['Product'], item['Location'], item['Quantity']))

    def destroy(self):
        print("closing window")
        self._serialMan.close()
        Frame.destroy(self)

def main():
    root = Tk()
    root.geometry("1000x300+300+300")
    app = WarehouseFrame()
    root.mainloop()

if __name__ == '__main__':
    main()

