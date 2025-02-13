import os
import sys

from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

from networksecurity.entity.artifact_entity import DataTransformationArtifact, ModelTrainerArtifact
from networksecurity.entity.config_entity import ModelTrainerConfig

from networksecurity.utils.ml_utils.model.estimator import NetworkModel
from networksecurity.utils.main_utils.utils import save_object, load_object
from networksecurity.utils.main_utils.utils import load_numpy_array_data,evaluate_models
from networksecurity.utils.ml_utils.metric.classification_metric import get_classification_score

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import r2_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import (
    AdaBoostClassifier,
    GradientBoostingClassifier,
    RandomForestClassifier
)
import mlflow
import dagshub
# Initialize DagsHub for MLFLOW tracking
dagshub.init(repo_owner='ankitmishra06', repo_name='NetworkSecurity', mlflow=True)


class ModelTrainer:
    def __init__(self,data_transformation_artifact:DataTransformationArtifact,model_trainer_config:ModelTrainerConfig):
        """
        Initializes the ModelTrainer class with the provided artifacts and configuration.
        """
        try:
            self.modle_trainer_config=model_trainer_config
            self.data_transformation_artifact=data_transformation_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    
    # mlflow.set_tracking_uri(uri="http://127.0.0.1:5000")
    def track_mlflow(self,best_model, classificationmetric):
        """
        Logs model performance metrics to MLflow.
        
        Args:
            best_model: Trained model to be logged.
            classificationmetric: Object containing F1-score, precision, and recall values.
        """
        with mlflow.start_run():
            # Log key classification metrics
            f1_score=classificationmetric.f1_score
            precision_score=classificationmetric.precision_score
            recall_score=classificationmetric.recall_score

            mlflow.log_metric("f1_score",f1_score)
            mlflow.log_metric("precision",precision_score)
            mlflow.log_metric("recall_score",recall_score)

            # Log the trained model in MLflow
            mlflow.sklearn.log_model(
                sk_model = best_model,
                artifact_path = "model"

            )

    
    def train_model(self, X_train, y_train,X_test,y_test):
        """
        Trains multiple models, evaluates their performance, and selects the best-performing model.

        Args:
            X_train: Training feature dataset.
            y_train: Training target labels.
            X_test: Testing feature dataset.
            y_test: Testing target labels.

        Returns:
            model_trainer_artifact: Contains details of the best model and its evaluation metrics.
        """
        # Define models and their respective hyperparameters
        models = {
            "Random Forest":RandomForestClassifier(verbose=1),
            "Decision Tree": DecisionTreeClassifier(),
            "Gradient Boosting":GradientBoostingClassifier(verbose=1),
            "Logistic Regression": LogisticRegression(verbose=1),
            "AdaBoost": AdaBoostClassifier()
        }
        params={
            "Decision Tree": {
                'criterion':['gini', 'entropy', 'log_loss'],
                # 'splitter':['best','random'],
                # 'max_features':['sqrt','log2'],
            },
            "Random Forest":{
                # 'criterion':['gini', 'entropy', 'log_loss'],
                
                # 'max_features':['sqrt','log2',None],
                'n_estimators': [8,16,32,128,256]
            },
            "Gradient Boosting":{
                # 'loss':['log_loss', 'exponential'],
                'learning_rate':[.1,.01,.05,.001],
                'subsample':[0.6,0.7,0.75,0.85,0.9],
                # 'criterion':['squared_error', 'friedman_mse'],
                # 'max_features':['auto','sqrt','log2'],
                'n_estimators': [8,16,32,64,128,256]
            },
            "Logistic Regression":{},
            "AdaBoost":{
                'learning_rate':[.1,.01,.001],
                'n_estimators': [8,16,32,64,128,256]
            }
            
        }
        # Evaluate models and their hyperparameters
        model_report:dict=evaluate_models(
            X_train=X_train,
            y_train=y_train,
            X_test=X_test,
            y_test=y_test,
            models=models,
            param=params
        )
        
        # Determine the best model based on evaluation scores
        best_model_score = max(sorted(model_report.values()))

        best_model_name = list(model_report.keys())[
            list(model_report.values()).index(best_model_score)
        ]
        best_model = models[best_model_name]

        # Evaluate the best model on training data
        y_train_pred=best_model.predict(X_train)
        classification_train_metirc=get_classification_score(y_true=y_train,y_pred=y_train_pred)

        # Track training metrics in MLflow
        self.track_mlflow(best_model,classification_train_metirc)

        # Evaluate the best model on testing data
        y_test_pred=best_model.predict(X_test)
        classification_test_metric=get_classification_score(y_true=y_test,y_pred=y_test_pred)

        # Track test metrics in MLflow
        self.track_mlflow(best_model=best_model,classificationmetric=classification_test_metric)

        # Load the preprocessor used during data transformation
        preprocessor = load_object(
            file_path=self.data_transformation_artifact.transformed_object_file_path
        )

        # Ensure directory exists before saving the model
        modle_dir_path = os.path.dirname(self.modle_trainer_config.trained_model_file_path)
        os.makedirs(modle_dir_path)

        # Create a network model wrapper with preprocessor and trained model
        Network_Model = NetworkModel(
            preprocessor=preprocessor, model= best_model
        )
        # Save trained model and preprocessor
        save_object(self.modle_trainer_config.trained_model_file_path,obj=Network_Model)
        save_object("final_model/model.pkl", best_model)

        # Create and log the ModelTrainerArtifact
        model_trainer_artifact=ModelTrainerArtifact(trained_model_file_path=self.modle_trainer_config.trained_model_file_path,
                             train_metric_artifact=classification_train_metirc,
                             test_metric_artifact=classification_test_metric,)
        logging.info(f"Model trainer artifact: {model_trainer_artifact}")
        return model_trainer_artifact
        


    def initiate_model_trainer(self)->ModelTrainerArtifact:
        """
        Initiates the model training process.

        Returns:
            ModelTrainerArtifact: Contains details of the trained model and its metrics.
        """
        try:
            # Get paths for transformed training and testing data
            train_file_path = self.data_transformation_artifact.transformed_train_file_path
            test_file_path = self.data_transformation_artifact.trasformed_test_file_path

            # Load transformed training and testing arrays
            train_arr = load_numpy_array_data(train_file_path)
            test_arr = load_numpy_array_data(test_file_path)

            # Load transformed training and testing arrays
            X_train, y_train, X_test, y_test=(
                train_arr[:,:-1],
                train_arr[:,-1],
                test_arr[:,:-1],
                test_arr[:,-1],
            )

            # Train the model and return the training artifact
            model_trainer_artifact=self.train_model(X_train=X_train,y_train=y_train,X_test=X_test,y_test=y_test)
            return model_trainer_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys)