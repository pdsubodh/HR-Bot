from utils import UpdatePdfFileVector, CreateDBCollection, ListAllDBCollection, DeleteDBCollection, UpdateEmplyeeVector, RetrievalQADBContent, UpdateTextFileVector

#DeleteDBCollection()
#UpdatePdfFileVector()
#VerifyDBContent('What is this document for?')
#RetrievalQADBContent('Provide all employee employee code and name only')
#RetrievalQADBContent('what is creche policy')
#CreateDBCollection()
#ListAllDBCollection()
#UpdateEmplyeeVector()
#UpdateTextFileVector()
#exit(1)

def show_menu():
    print("\n\n")    
    print("======================================================================")    
    print("=            Backoffice - RAG:: Enterprise Human Resource            =")
    print("======================================================================")     
    print("######   1. Update Enterprise Policies (.pdf Format)    ######")
    print("######   2. Update Employee Details (.xlsx Format)      ######")
    print("######   3. UpdateUpdate Other Details (.txt Format)    ######")
    print("######   4. Verify Content in Knowledgebase             ######")  
    print("----------------------------------------------------------------------")  
    print("----------------------- Admin Tool -----------------------------------")  
    print("######   5. Create Databases                            ######")
    print("######   6. List  All Databases                         ######") 
    print("######   7. Delete existing Databases                   ######")  
    print("######   8. Exit or Quit                                ######")
    print("______________________________________________________________________")

def main():
    while True:
        show_menu()
        choice = input("Enter your choice (1-8): ")

        if choice == '8':
            print("Exiting... Goodbye!")
            break

        if choice not in ['1', '2', '3', '4', '5', '6','7','8']:
            print("Invalid choice. Try again!")
            continue


        if choice == '1':
                UpdatePdfFileVector()
        elif choice == '2':
                UpdateEmplyeeVector()
        elif choice == '3':
                UpdateTextFileVector()    
        elif choice == '4':
                RetrievalQADBContent("Provide all employee employee code and name only")
        elif choice == '5':
                CreateDBCollection()       
        elif choice == '6':
                ListAllDBCollection() 
        elif choice == '7':
                DeleteDBCollection()
        

if __name__ == "__main__":
    main()
