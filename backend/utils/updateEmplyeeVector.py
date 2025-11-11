from utils.common import processStartMsg, processEndMsg
import pandas as pd
from qdrantDbConnection import getQdrantClient
from langchain_qdrant import QdrantVectorStore
from langchain_openai import OpenAIEmbeddings


import shutil
import os
from dotenv import load_dotenv
load_dotenv()

# Load credentials & Configurations ---------------------------------------------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")

sourcePath = os.path.join(os.getcwd(), "backend/documentSource/unprocessed/xlsx")
targetPath = os.path.join(os.getcwd(), "backend/documentSource/processed/xlsx")

# --------------------------------------------------------------------------------------------------



def moveProcessfile():
    print("Processced File(s):")
    for item in os.listdir(sourcePath):
        if item.lower().endswith(('.xlsx')):
            print("  - "+item)
            src_path = os.path.join(sourcePath, item)
            dest_path = os.path.join(targetPath, item)

            # Move file or directory
            shutil.move(src_path, dest_path)

    
def UpdateEmplyeeVector():
    processStartMsg("Employee file start updating in vector database...")
    try:
        excel_file = "employee_data.xlsx"

        for fileName in os.listdir(sourcePath):
            if fileName.lower().endswith(('.xlsx')):
                #print("  - "+fileName)
                dataFrame = __ingestFromExcel(fileName)
                if(len(dataFrame) > 0):
                   #print(f"Loaded {len(df)} employees from Excel")
                    i=0
                    for _, row in dataFrame.iterrows():
                        
                        #Clean Data
                        employee = __cleanEmployeeData(row.to_dict())
                        #print(employee)

                        #Generate Context Text
                        contextText = __generateEmployeeContext(employee)
                        #print(contextText)

                        #Add to vector database
                        __addToVectorDb(contextText, employee)
                        i = i+1
                        print(f"#{i}:: {row['EmployeeCode']}-{row['EmployeeName']}")
                        

            
            #please uncomment below line
            #sleep(2)
            
        #----- Move File(s) in Processed folder ---------------
        moveProcessfile()
        
        
    except Exception as e:
        print(f"Error in UpdateEmplyeeVector: {e}")
        

def __ingestFromExcel(excelFile: str):
    
    try:
        filePath = os.path.join(sourcePath, excelFile)
        dataFrame = pd.read_excel(filePath)
        return dataFrame
    except Exception as e:
        print(f"Error in __ingest_from_excel: {e}")
    

def __cleanEmployeeData(employee: dict) -> dict:
    try:
        """Convert date fields to ISO format and clean data."""
        for date_field in ["DateOfJoining"]:
            value = employee.get(date_field)
            if pd.notna(value):
                employee[date_field] = pd.to_datetime(value).strftime("%Y-%m-%d")
            else:
                employee[date_field] = None
                
        return employee

    except Exception as e:
        print(f"Error in __cleanEmployeeData: {e}")

def __generateEmployeeContext(employee: dict) -> str:
    try:
        
        """Create text context for embeddings."""
        text = f"""
            Employee Code: {employee.get('EmployeeCode')}
            Employee Name: {employee.get('EmployeeName')}
            Gender: {employee.get('Gender')}            
            Mobile Number: {employee.get('Mobile')}
            Email ID: {employee.get('Email')}
            Date of Joining: {employee.get('DateOfJoining')}
            Employee Status: {employee.get('EmployeeStatus')}
            Country: {employee.get('Country')}
            State: {employee.get('State')}
            Organisation Unit: {employee.get('OrganisationUnit')}
            Department: {employee.get('Department')}
            Sub-Department: {employee.get('SubDepartment')}
            Designation: {employee.get('Designation')}
            Grade: {employee.get('Grade')}
            Role: {employee.get('Role')}
            Reporting Manager Name: {employee.get('ReportingManagerEmployeeName')}
            Reporting Manager Employee Code: {employee.get('ReportingManagerEmployeeCode')}

            Summary:
            {employee.get('EmployeeName')} (Employee Code: {employee.get('EmployeeCode')}) works as a {employee.get('Designation')} 
            in the {employee.get('Department')} department under {employee.get('ReportingManagerEmployeeName')}. 
            They joined on {employee.get('DateOfJoining')} and currently hold {employee.get('EmployeeStatus')} status.
            Based in {employee.get('State')}, {employee.get('Country')}, they perform the role of {employee.get('Role')} 
            within the {employee.get('OrganisationUnit')} unit.
            """
        return text.strip()
    except Exception as e:
        print(f"Error in generating employee context: {e}")
        return ""

def __addToVectorDb(contextText: str, employee: dict):
    try:
        
        #----- Initialize embedding model ---
        embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL, openai_api_key=OPENAI_API_KEY)
        
        #-----Store documents in Qdrant Cloud ---------------
        clientObj = getQdrantClient()
        vectorstore = QdrantVectorStore(
            client=clientObj,
            collection_name=COLLECTION_NAME,
            embedding=embeddings,
            )
        vectorstore.add_texts([contextText], metadatas=[employee])
        #print(f"Successfully stored:: Employee: {employee.get('EmployeeCode')} - {employee.get('EmployeeName')} in collection: {COLLECTION_NAME}")

    except Exception as e:
        print(f"Error in adding to vector DB: {e}")
        #print(f"Error in adding to vector DB:: Employee: {employee.get('EmployeeCode')} - {employee.get('EmployeeName')} in collection: {COLLECTION_NAME}")