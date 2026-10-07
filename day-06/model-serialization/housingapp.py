import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import pickle
import os.path

class Housing(object):

    def __init__(self, datasource):
        self.datasource = datasource
        self.data = []
        self.X_train = []
        self.X_test = []
        self.y_train = []
        self.y_test = []
        self.model = []
        
    def acquire(self):
        try:
            self.data = pd.read_csv(self.datasource)
            return (True, '', 'Read the file'.format(self.datasource))
        except Exception as ErrorMessage:
            return (False, '', ErrorMessage)

    def prepare(self):
        return (True, '', 'Nothing to prepare')

    def split(self):
        #Setting the target column
        target = 'Price'
        y = self.data['Price']
        #Get the predictor columns
        droplist = [target, 'Address']
        predictors = self.data.drop(droplist, axis=1).columns
        X = self.data[predictors]
        # make the split
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(X, y, test_size=0.1, random_state=100)

    def train(self):
        try:
            self.model = LinearRegression()
            self.model.fit(self.X_train, self.y_train)
            return(True, self.model, 'Model created successfully')
        except:
            return(False, '', 'Model creation failed')
        
    def getparams(self):
        return {'intercept':self.model.intercept_, 'slope':self.model.coef_}
        
    def savemodel(self, path='.'):
        with open(os.path.join(path, "housing_model.pkl"), "wb") as file:
            pickle.dump(self.model, file)

    def loadmodel(self, path):
        with open(os.path.join(path, "housing_model.pkl"), "rb") as file:
            self.model = pickle.load(file)

    def getmodel(self):
        return self.model

    def getpredictions(self, values=[100000, 15, 5, 3, 50000]):
        inputs = []
        inputs.append(values)
        return self.model.predict(inputs)
    
    def pipeline(self):
        self.model.prepare()
        self.model.split()
        self.model.train()
        return {'intercept':self.model.intercept_, 'slope':self.model.coef_}

    
# --------------------------------------------------------------------

if __name__ == '__main__':

    file = r'USA_Housing.csv'
    h = Housing(file)
    print('Data Aquisition:   >> ', h.acquire())
    print('Data Preparation:  >> ', h.prepare())
    print('Splitting:         >> ', h.split())
    print('Training:          >> ', h.train())
    print('Parameters:        >> ', h.getparams())
    print('Save Model:        >> ', h.savemodel())