import util
import sklearn.datasets
import sklearn.metrics
#import sklearn.cross_validation
import sklearn.svm
import sklearn.naive_bayes
import sklearn.neighbors
from colorama import init
from termcolor import colored
import sys
import os
import glob
from sklearn.model_selection import train_test_split as cross_validation




def main():
    init()

    # get the dataset
    print (colored("Where is the dataset?", 'cyan', attrs=['bold']))
    print (colored('warning: files might get deleted if they are incompatible with utf8', 'yellow'))
    ans = sys.stdin.readline()
    # remove any newlines or spaces at the end of the input
    print (ans)
    path = ans.strip('\n')
    if path.endswith(' '):
        path = path.rstrip(' ')
        
        
    # preprocess data into two folders instead of 6
    print (colored("Reorganizing folders, into two classes", 'cyan', attrs=['bold']))
    reorganize_dataset(path)

    print ('\n\n')

    # do the main test
    main_test(path)


def reorganize_dataset(path):
    likes = ['rec.sport.hockey', 'sci.crypt', 'sci.electronics']
    dislikes = ['sci.space', 'rec.motorcycles', 'misc.forsale']

    folders = glob.glob(os.path.join(path, '*'))
    #print (folders,likes,dislikes)
    
    if len(folders) == 2:
        return
    else:
        # create `likes` and `dislikes` directories
        if not os.path.exists(os.path.join(path, 'likes')):
            os.makedirs(os.path.join(path, 'likes'))
        if not os.path.exists(os.path.join(path, 'dislikes')):
            os.makedirs(os.path.join(path, 'dislikes'))

        for like in likes:
            files = glob.glob(os.path.join(path, like, '*'))
            #print (path,like)
            
            for f in files:
                parts = f.split(os.sep)
                name = parts[len(parts) - 1]
                newname = like + '_' + name
                print (newname,name)
                os.rename(f, os.path.join(path, 'likes', newname))
                print("added to likes")
            #os.rmdir(os.path.join(path, like))

        for like in dislikes:
            files = glob.glob(os.path.join(path, like, '*'))
            for f in files:
                parts = f.split(os.sep)
                name = parts[len(parts) - 1]
                newname = like + '_' + name
                os.rename(f, os.path.join(path, 'dislikes', newname))
                print("added to dislikes")
            #os.rmdir(os.path.join(path, like))
            
            


def main_test(path=None):
    dir_path = path or 'dataset'

    remove_incompatible_files(dir_path)

    print ('\n\n')

    # load data
    print (colored('Loading files into memory', 'green', attrs=['bold']))
    files = sklearn.datasets.load_files(dir_path)
    #print (files)

    # refine all emails
    #print(files.data)
    print (colored('Refining all files', 'green', attrs=['bold']))
    util.refine_all_emails(files.data)

    # calculate the BOW representation
    print (colored('Calculating BOW', 'green', attrs=['bold']))
    word_counts = util.bagOfWords(files.data)

    # TFIDF
    print (colored('Calculating TFIDF', 'green', attrs=['bold']))
    tf_transformer = sklearn.feature_extraction.text.TfidfTransformer(use_idf=True).fit(word_counts)
    X = tf_transformer.transform(word_counts)

    print ('\n\n')

    # create classifier
    # clf = sklearn.naive_bayes.MultinomialNB()
    # clf = sklearn.svm.LinearSVC()
    n_neighbors = 11
    weights = 'uniform'
    weights = 'distance'
    clf = sklearn.neighbors.KNeighborsClassifier(n_neighbors, weights=weights)

    # test the classifier
    print ('\n\n')
    print (colored('Testing classifier with train-test split', 'magenta', attrs=['bold']))
    test_classifier(X, files.target, clf, test_size=0.2, y_names=files.target_names, confusion=False)


def remove_incompatible_files(dir_path):
    # find incompatible files
    print (colored('Finding files incompatible with utf8: ', 'green', attrs=['bold']))
    incompatible_files = util.find_incompatible_files(dir_path)
    print (colored(len(incompatible_files), 'yellow'), 'files found')

    # delete them
    if(len(incompatible_files) > 0):
        print (colored('Deleting incompatible files', 'red', attrs=['bold']))
        util.delete_incompatible_files(incompatible_files)


def test_classifier(X, y, clf, test_size=0.4, y_names=None, confusion=False):
    # train-test split
    #print ('test size is: %2.0f%%' % (test_size * 100))
    print ('test size is: {:.2f}'.format(test_size * 100 ))

    X_train, X_test, y_train, y_test = cross_validation(X, y, test_size=test_size)

    clf.fit(X_train, y_train)
    y_predicted = clf.predict(X_test)
    
    #print (y_predicted,X_train, y_train)

    if not confusion:
        print (colored('Classification report:', 'magenta', attrs=['bold']))
        print (sklearn.metrics.classification_report(y_test, y_predicted))
    else:
        print (colored('Confusion Matrix:', 'magenta', attrs=['bold']))
        print (sklearn.metrics.confusion_matrix(y_test, y_predicted))

if __name__ == '__main__':
    main()
