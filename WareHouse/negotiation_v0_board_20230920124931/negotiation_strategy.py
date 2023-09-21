'''
This file contains the NegotiationStrategy class which is responsible for generating the negotiation strategy report.
'''
import pandas as pd
class NegotiationStrategy:
    def __init__(self, df):
        self.df = df
    def calculate_savings(self):
        if 'Current Cost' not in self.df.columns:
            raise Exception("'Current Cost' column not found in the input file.")
        self.df['Savings'] = self.df['Current Cost'] * 0.10
        self.df['New Cost'] = self.df['Current Cost'] - self.df['Savings']
    def generate_report(self):
        self.calculate_savings()
        self.df.to_excel('Negotiation_Strategy_Report.xlsx', index=False)