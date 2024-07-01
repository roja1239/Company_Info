'''
Install these Libraries in cmd : streamlit,openai,langchain,langchain_community,google-search-results,wikipedia

# Find more emojis here: https://www.webfx.com/tools/emoji-cheat-sheet/

'''
import streamlit as st
import openai
import re
import os
import langchain
from langchain import OpenAI, PromptTemplate
from langchain.agents import load_tools, initialize_agent
from langchain_community.utilities import SerpAPIWrapper
import warnings
from bs4 import BeautifulSoup
import requests
from requests.exceptions import ConnectionError

# Function to interact with ChatGPT
def chat_with_gpt(message):
    # Monkey patch the BeautifulSoup constructor
    original_bs4_init = BeautifulSoup.__init__
    def new_bs4_init(self, *args, **kwargs):
        if 'features' not in kwargs:
            kwargs['features'] = 'lxml'
        original_bs4_init(self, *args, **kwargs)

    BeautifulSoup.__init__ = new_bs4_init

    warnings.filterwarnings("ignore", category=DeprecationWarning)

    # OpenAi key and SerpApi Key
    # SerpApi key for the GoogleSearch Results
    os.environ['OPENAI_API_KEY'] = 'sk-proj-KipUk3PDu73OeMVMoXKAT3BlbkFJ0kqDXq1j79WNEwLbV25k'
    os.environ['SERPAPI_API_KEY'] = 'fdcbacc41ba60ba1c5665b327713c6a89fc36e6c8a71828c6726457bba34961e'

    # Load tools
    tools = load_tools(["serpapi", "wikipedia"], llm=OpenAI(api_key=os.environ['OPENAI_API_KEY']))

    # Initialize agent
    agent = initialize_agent(tools, agent="zero-shot-react-description", llm=OpenAI(api_key=os.environ['OPENAI_API_KEY']))

    # company name 
    company_name = message

    # Define your PromptTemplate for basic company information
    basic_info_template = PromptTemplate.from_template(
        "Retrieve the contact details and address for the company {company_name}. The details should include:\n"
        "- Email\n"
        "- Website\n"
        "- Address\n"
        "- City\n"
        "- Products\n"
        "- Services\n"
        "- Revenue\n"
        "- Competitors\n"
        "- Branches\n"
        "- Careers\n"
        "Please ensure the information is accurate and up-to-date."
    )

    financial_info_template = PromptTemplate.from_template(
        "Extract financial information about {company_name}: Current Stock Price in USD, Revenue in Dollar and in Rupees, Operating Income in Dollar and in Rupees, Net Income in Dollar and in Rupee, Total Assets in Dollar and in Rupee, Total Equity in Dollar and in Rupee."
    )

    # Define your PromptTemplate for additional information
    additional_info_template = PromptTemplate.from_template(
        "Extract additional information about {company_name}: Number of Employees."
    )

    # Define validation functions for phone number and email
    def validate_phone_number(phone):
        # Phone number should be a 10-digit number with an optional country code
        pattern = re.compile(r"^\+?\d{1,3}?\d{10}$")
        return pattern.match(phone)

    def validate_email(email):
        # Email should contain @ once
        pattern = re.compile(r"^[^@]+@[^@]+\.[^@]+$")
        return pattern.match(email)

    # Define extraction functions for email and phone number
    def extract_email(line):
        match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", line)
        return match.group(0) if match else None

    def extract_phone_number(line):
        match = re.search(r"\+?\d{1,3}?\d{10}", line)
        return match.group(0) if match else None

    # Run the agent with each formatted prompt separately and print results
    # Basic Information
    basic_info_result = agent.run(basic_info_template.format(company_name=company_name))
    #print(basic_info_result)
    # print("Basic Information:")
    try:
        for line in basic_info_result.split("\n"):
            if ": " in line:
                key, value = line.split(": ", 1)
                if "phone" in key.lower() or "contact" in key.lower():
                    phone = extract_phone_number(value)
                    if phone:  # Check if a phone number was extracted
                        value = phone if validate_phone_number(phone) else "N/A"
                    else:
                        value = "N/A"  # No phone number was extracted
                elif "email" in key.lower():
                    email = extract_email(value)
                    if email:  # Check if an email was extracted
                        value = email if validate_email(email) else "N/A"
                    else:
                        value = "N/A"  # No email was extracted
                return(f"/n{key}: {value}")
            else:
                return(basic_info_result)
    except ConnectionError as e:
        print("Connection Error occured : ",e)
        return None


# Streamlit App
def main():
    st.title("Company Info Extracter 🏢 ")
    st.markdown(
        "This is a Company Info 👾 Extracter . "
    )
    user_input = st.text_input("Enter Company Name  : ")
    if user_input:
        st.write("Comapany  : ", user_input)
        reply = chat_with_gpt(user_input)
        st.write("CompanyInfo :", reply)

if __name__ == "__main__":
    main()