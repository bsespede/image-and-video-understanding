import os
import numpy as np
import cv2 as cv

if __name__ == '__main__':
    scriptDirectory = os.path.dirname(__file__)
    pikeData = np.load('hu_moments/traindata_pike.npy')
    straightData = np.load('hu_moments/traindata_straight.npy')
    tuckData = np.load('hu_moments/traindata_tuck.npy')

    # general stuff
    trainPercentage = 0.3 #TODO: when increasing it always predicts  straights, data is unbalanced
    pikeFrames, pikeFeatures = pikeData.shape
    straightFrames, straightFeatures = straightData.shape
    tuckFrames, tuckFeatures = tuckData.shape

    # training related
    totalTrainingPikes = int(pikeFrames * trainPercentage)
    totalTrainingStraights = int(straightFrames * trainPercentage)
    totalTrainingTucks = int(tuckFrames * trainPercentage)

    pikeTrainingData = pikeData[:totalTrainingPikes, :].astype(np.float32)
    straightTrainingData = straightData[:totalTrainingStraights, :].astype(np.float32)
    tuckTrainingData = tuckData[:totalTrainingTucks, :].astype(np.float32)

    pikeTrainingLabels = np.full((1, totalTrainingPikes), 0, dtype=np.int64)
    straightTrainingLabels = np.full((1, totalTrainingStraights), 1, dtype=np.int64)
    tuckTrainingLabels = np.full((1, totalTrainingTucks), 2, dtype=np.int64)

    trainingLabels = np.concatenate((pikeTrainingLabels, straightTrainingLabels, tuckTrainingLabels), axis=1)

    trainingData = np.copy(pikeTrainingData)
    trainingData = np.append(trainingData, straightTrainingData, axis=0)
    trainingData = np.append(trainingData, tuckTrainingData, axis=0)

    # train svm
    svm = cv.ml.SVM_create()
    svm.setType(cv.ml.SVM_C_SVC)
    svm.setKernel(cv.ml.SVM_LINEAR) # TODO: try other interpolation methods
    svm.setTermCriteria((cv.TERM_CRITERIA_MAX_ITER, 100, 1e-6))
    svm.train(trainingData, cv.ml.ROW_SAMPLE, trainingLabels)

    # test related
    totalTestPikes = int(pikeFrames * trainPercentage)
    totalTestStraights = int(straightFrames * trainPercentage)
    totalTestTucks = int(tuckFrames * trainPercentage)

    pikeTestData = pikeData[totalTestPikes:, :].astype(np.float32)
    straightTestData = straightData[totalTestStraights:, :].astype(np.float32)
    tuckTestData = tuckData[totalTestTucks:, :].astype(np.float32)

    confusionMatrix = np.zeros((3, 3), dtype=np.int64)

    # test svm_svm
    for pikeFeatureVector in pikeTestData:
        response = svm.predict(pikeFeatureVector.reshape((1, pikeFeatures)))[1]
        convertedResponse = int(response[0][0])
        confusionMatrix[0, convertedResponse] += 1

    for straightFeatureVector in straightTestData:
        response = svm.predict(straightFeatureVector.reshape((1, straightFeatures)))[1]
        convertedResponse = int(response[0][0])
        confusionMatrix[1, convertedResponse] += 1

    for tuckFeatureVector in tuckTestData:
        response = svm.predict(tuckFeatureVector.reshape((1, tuckFeatures)))[1]
        convertedResponse = int(response[0][0])
        confusionMatrix[2, convertedResponse] += 1

    print("Confusion matrix:", confusionMatrix) # indices of conf matrix: 0 pike, 1 straight, 2 tuck
    np.save('confusion_matrix.npy', confusionMatrix)

