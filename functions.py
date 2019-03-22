import os
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
sns.set_style('darkgrid')



# CLEAN COLUMN NAMES 
def clean_column_name(df=pd.DataFrame()):
    columns = [i.replace(' ','_').lower() for i in df.columns]
    df.columns=columns
    return df


# MAKE BUG DATA COMPATIBLE WITH METRICS DATA
def aggregate_impBug_package_name(BugDf = pd.DataFrame()):
    group = BugDf.groupby(['package_name','type_name','method_name'])['code_smell'].count()
    group = group.reset_index()
    group['name'] = ''
    group['name'] = group.apply(lambda row: '%s.%s.%s'%(row['package_name'],row['type_name'],row['method_name']),axis=1)
    return group

def aggregate_designBug_package_name(BugDf = pd.DataFrame()):
    group = BugDf.groupby(['package_name','type_name'])['code_smell'].count()
    group = group.reset_index()
    group['name'] = ''
    group['name'] = group.apply(lambda row: '%s.%s'%(row['package_name'],row['type_name']),axis=1)
    return group



#### Reading functions :
#- Reads the files for the project
#- Directory structure :
#    - for metrics data : 'data/metrics/project_name/(project_name 0.0.0.csv)
#    - for bugs data    : 'data/bugs/project_name/project_name version(0.0)/




# MAKE METRICS DICTIONARY : project.version.df
def read_metrics_file(file):
    path = os.getcwd()+'/data/metrics/'+file
    files = os.listdir(path)
    metrics_dict = dict()

    for file in files:
        
        ver_name = 'v'+file.split()[1].split('.')[1]
        metrics_dict[ver_name] = pd.read_csv(path+'/'+file)
        metrics_dict[ver_name] = clean_column_name(metrics_dict[ver_name])
    
    return metrics_dict

# MAKE BUGS DICTIONARY : project.version.df
# WILL RETURN A SINGLE BUGS DICTIONARY ( COMBO OF DESIGN AND IMPL BUGS)
def read_bugs_file(file):
    path = os.getcwd()+'/data/bugs/'+file+'/'
    files = os.listdir(path) #will list file names
    bugs_dict = dict()

    for f in files:
        nPath = path+f+'/'
        ver_name = 'v'+f.split('.')[1]
        
        implementationSmells = pd.read_csv(nPath+'implementationCodeSmells.csv')
        designCodeSmells = pd.read_csv(nPath+'designCodeSmells.csv')
    
        implementationSmells = clean_column_name(implementationSmells)
        designCodeSmells = clean_column_name(designCodeSmells)

        implementationSmells = aggregate_impBug_package_name(implementationSmells)
        designCodeSmells = aggregate_designBug_package_name(designCodeSmells)

        #MERGING DESIGN AND IMPLEMENTATION BUGS
        bugsdata = implementationSmells.merge(designCodeSmells,how='outer')
        bugs_dict[ver_name] = bugsdata
        
    return bugs_dict



#This single Method is to be used:
#Calls:
    # -read_metrics_file()
    # -read_bugs_file()

def process_project_data(file,exploratory=False):
    fileMetricsDict = read_metrics_file(file)
    fileBugDict = read_bugs_file(file)
    
    data = dict()
    for ver in fileMetricsDict.keys():
        
        bug = fileBugDict[ver]
        met = fileMetricsDict[ver]
        data[ver] = met.merge(bug,how='outer',on='name')
        
        # fill nan 
        #data[ver].code_smell = data[ver].code_smell.apply(lambda x: x if pd.notnull(x) else 0)
        data[ver] = data[ver].fillna(value=0)
        data[ver]['bug'] = data[ver].code_smell.apply(lambda x: 1 if x>0 else 0)
        
        data[ver] = data[ver].rename(columns={'countclasscoupled':'cbo',
                                    'maxinheritancetree':'dit',
                                    'sumcyclomatic':'wmc',
                                    'countclassderived':'noc',
                                    'percentlackofcohesion':'lcom',
                                    'countdeclmethodall':'rfc',
                                    'cyclomatic':'cyclomatic',
                                            })
        if exploratory == True:
            data[ver].drop('name',axis=1,inplace=True)
            data[ver].drop('kind',axis=1,inplace=True)
            data[ver].drop('countline',axis=1,inplace=True)
            data[ver].drop(['countlinecode','package_name','type_name','method_name'],axis=1,inplace=True)
           
    return data



## REMOVE OUTLIERS
def limit_data_dict(dic = dict()):
   
    for ver in dic :
        df = dic[ver]
        df = df[df.rfc<60]
        df = df[df.wmc<60]
        df = df[df.noc<60]
        df = df[df.lcom<60]
        df = df[df.cbo<60]
        dic[ver] = df
    return dic



###############################################
### Plotting Methods:
#def create_heat_plots(df=pd.DataFrame(),proj_name=''):

def plot_heatMaps(df=pd.DataFrame(),proj_name=''):
    path = os.getcwd()+'/plots/'+proj_name+'/'
    fType = 'heatmap'
    
    if proj_name!='':
        path = os.getcwd()+'/plots/'+proj_name
        try:
            os.mkdir(path)
        except:
            pass
    
    for ver in df:  
        corr = df[ver].corr()
        
        title = '%s  %s_%s'%(fType.upper(),proj_name,ver)
        
        f,ax = plt.subplots(figsize=(8,8))
        ax.set_title(title)
        mask = np.zeros_like(corr)
        mask[np.triu_indices_from(mask)] = True

        with sns.axes_style("white"):
            ax = sns.heatmap(corr, mask=mask, square=True, annot=True,linewidths=1)
            plt.show()
        if proj_name!='':
            #print('saving at : %s/%s.jpg'%(path,title))
            f.savefig('%s/%s.jpg'%(path,title))


#def create_reg_plots(data=dict(),checkVar='',vsVarList=[],proj_name=''):
def plot_regressions(data=dict(),checkVar='',vsVarList=[],proj_name='',ylim=120):
    
    fType = 'regplot'
    path = os.getcwd()+'/plots/'+proj_name+'/'+fType+'/'
    
    #Make Directory
    if proj_name!='':
        try:
            os.mkdir(path)
        except:
            pass
    
    # for every version
    for ver in data:
        print('\n',ver)
        df = data[ver]
        
        # for every variable in vsVarList
        for v in vsVarList:
            title = '%svs%s  %s_%s'%(checkVar.upper(),v.upper(),proj_name,ver)
            
            f,ax = plt.subplots(figsize=(10,7))
            ax.set_title(title)
            ax.set_ylim([0,ylim])
            sns.regplot(data=df,y=checkVar,x=v,fit_reg=True)
            plt.show()
            
            if proj_name!='':
                #print('saving at : %s/%s_%s.jpg'%(path,fType,ver))
                f.savefig('%s/%s.jpg'%(path,title))



            