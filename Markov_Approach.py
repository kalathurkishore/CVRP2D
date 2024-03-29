import pandas as pd
from inspect import signature
import numpy as np
import glob
import torch
from torch import nn, optim
from torch.autograd import Variable
import torch.utils.data as data_utils
import itertools
from MarkovModel import*
from CVRPPD_model import *
from CVRPPD_LSTM_model import *
from Constraint_Solver_using_Gurobi import *
formatter = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(filename='EvaluationAdditiveModels.log', level=logging.INFO,format=formatter)

# load data
if __name__ == "__main__":
    npzfile = np.load("/DATA/anonymous/CVRP2D/data/daily_stops_data.npz",allow_pickle=True,)
    stops = npzfile['stops_list'] # 201 length list indicating which stops are active for each day
    #print(stops)
    n_vehicles= npzfile['nr_vehicles'] # n_vehicles for each day
    weekday= npzfile['weekday'] # categorical input
    capacities = npzfile['capacities_list']# vehicle capacity
    demands = npzfile['demands_list'] # demands of each active stops
    #print(demands)
    pickups = np.load("/DATA/anonymous/CVRP2D/data/pickup_list_data.npy")  # pickups at each active stops
    #demands = np.load("/DATA/anonymous/CVRP2D/data/pickup_demand_list_data.npy")
    npzfile = np.load("/DATA/anonymous/CVRP-DP/Data-Driven-VRP/data/daily_routematrix_data.npz", allow_pickle=True)
    opmat = npzfile['incidence_matrices'] # solutions for each day as an incidence matrix
    stop_wise_days = npzfile['stop_wise_active'] 
    distance_mat = np.load("/DATA/anonymous/CVRP2D/data/Distancematrix.npy")
    #print(distance_mat)
    edge_mat = np.load("/DATA/anonymous/CVRP2D/data/edge_category_data.npy")

    
    smoothing,exp = 0.1,0.7
    lookback = 150 #30,10, 7,1,3,100,150
    omega  = 1
    
    models_dict = {
        "markov":TwoStageVRP(MarkovCounter,weekly=False, 
        beta=1, smoothing_value= smoothing, exp= exp ),

    "markovweekly":TwoStageVRP(MarkovCounter,weekly=True,
     beta=1, smoothing_value= smoothing, exp= exp ),
    "distance":TwoStageVRP(MarkovCounter,beta=0 )
    }

    test_days = [154,160, 166, 173, 180, 187, 194,
    155,161, 167, 174, 181, 188, 195,
    149,156, 168, 175, 182, 189, 196,
    150,162, 169, 176, 183, 190, 197,
    157,163, 170, 177, 184, 191, 198, 
    158, 164, 171, 178, 185, 192, 199,
    159, 165, 172, 179, 186, 193, 200]
    # for iteration in range(1):
    lst = []
    for t in test_days:
        for m in models_dict:
            model = models_dict[m]
            ev = model.evaluation(distance_mat, stops[:(t+1)],
            weekday[:(t+1)],n_vehicles[:(t+1)],
            opmat[:(t+1)], stop_wise_days,  demands[t], pickups[t], capacities[t:(t+1)],
            capacitated = True,omega= omega)#added pickups
            lst.append({"Day":t,"Model":m,
            "smoothing":smoothing,"exp":exp,
            "lookback":lookback,
            'omega':omega,
            "bceloss":ev[2],"training_bcelos":ev[3],
            "Arc Difference":ev[0][0],"Arc Difference(%)":ev[0][1],
            "Route Difference":ev[1][0],
            "Route Difference(%)":ev[1][1],"Distance":ev[4],
            "Comment":ev[5] })
    df = pd.DataFrame(lst)
    filename= 'MarkovModels_new.csv'
    with open(filename, 'a') as f:
        df.to_csv(f, header=f.tell()==0,index=False)


            
