
import numpy as np

def get_children(dist_arr, fired_nodes, src_bc):
        arr_node_rdds = []
        #print('dist_arr', dist_arr)
        is_src=False
        for i in range(len(dist_arr)):
            if dist_arr[i][0] in fired_nodes:
                #print('node', dist_arr[i][0], 'in node_list, continue\n ')
                continue
            node_id_bc = sc.broadcast(dist_arr[i][0])
            A = dist_arr[i][1]
            A_bc = sc.broadcast(A)
            temp_rdd_i = rdd_graph_shell.filter(lambda x: x[0]==node_id_bc.value)
            print('node_id_bc:', node_id_bc.value, 'i:', i, 'temp_rdd_i:', temp_rdd_i.collect())
            if node_id_bc.value==src_bc.value:
                    is_src=True
                    print('in node_id_bc == src_bc')               
            print('src_bc:', src_bc.value)
            temp_rdd_i = temp_rdd_i.mapValues(partial(activate, A_bc=A, D_bc=D, F_bc=F, src_bc=src_bc.value, is_src=is_src)).collect()
            if temp_rdd_i!=[]:
                arr_node_rdds.append(temp_rdd_i[0][1])
                fired_nodes.append(temp_rdd_i[0][0])
            #print('arr_node_rdds:', arr_node_rdds)
        #fired_nodes.extend(arr_node_rdds)
        return arr_node_rdds


    
#return the rdd with the values' activations updated with the Decay factor and only if that amount is more than the threshold F
def activate(val_list, A_bc, D_bc, F_bc, src_bc, is_src=False):
        res = []
        for v in val_list:
            print('v:', v)
            if v==src_bc:
                        continue
            if is_src:
                A=A_bc*v[1]
            else:
                A=A_bc*v[1]*D_bc
            print(A_bc, "*", v[1], "*", D_bc)
            #A=v[1]*D_bc.value
            if A>F_bc:
                print('A:', A)
                res.append((v[0], A))
        return res


    
from functools import partial
def walk_path(A, D, F, src, rdd_graph_shell, n=5):
        src_bc = sc.broadcast(src)
        rdd_src = rdd_graph_shell.filter(lambda x: x[0]==src_bc.value)
        A_bc = sc.broadcast(A) #Activation value is 1 (100%) for the source, will be changed to updated values with subsequent nodes
        D_bc = sc.broadcast(D)
        F_bc = sc.broadcast(F)
        fired_nodes=[] # a list of the nodes whose children have already been looked up
        init_dist_arr = rdd_src.mapValues(partial(activate, A_bc=A, D_bc=D, F_bc=F, src_bc=src_bc.value)).collect()[0][1]
        init_z=get_children(init_dist_arr, fired_nodes, src_bc)
        z=init_z[1:]
        node_arrs = []
        while z!=[]:
                for i in range(len(z)):
                        a = activate(z[i], A_bc=A, D_bc=D, F_bc=F, src_bc=src_bc)
                        node_arrs.extend(a)
                z=get_children(node_arrs, fired_nodes, src_bc)
        node_arrs_rdd = sc.parallelize(node_arrs)
        init_z_rdd = sc.parallelize(init_z)
        init_z_rdd = init_z_rdd.flatMap(lambda x: x)
        node_arrs_res = node_arrs_rdd.union(init_z_rdd)
        node_arrs_res2 = node_arrs_res.combineByKey(li, app, ext)
        
        #node_arrs_res3 = node_arrs_res2.mapValues(max)
        node_arrs_res3 = node_arrs_res2.mapValues(lambda x: np.mean(x))
        node_arrs_res4 = node_arrs_res3.filter(lambda x: x[0][1]=='m')
        #TOP_N_RECOMMENDATIONS = node_arrs_res4.sortBy(lambda x: x[1]).collect()[-(n+1):-1]
        TOP_N_RECOMMENDATIONS = node_arrs_res4.sortBy(lambda x: x[1])
        return TOP_N_RECOMMENDATIONS



def max(arr):
        max=0
        for x in arr:
                if x>max:
                        max=x
        return max




if __name__=="__main__":
        inv_USER_MOVIE_NETWORK_Gaussian = USER_MOVIE_NETWORK_Gaussian.map(lambda x: (x[1][0], (x[0], x[1][1])))
        USER_MOVIE_NETWORK_Gaussian2 = USER_MOVIE_NETWORK_Gaussian.union(inv_USER_MOVIE_NETWORK_Gaussian) #have pairs A-B and B-A
        src = ('2', 'u')
        
        rdd_graph_shell = USER_MOVIE_NETWORK_Gaussian2.combineByKey(li, app, ext)
     
        A=1 #Activation value for source
        D=.8 #Decay factor
        F=0 #Activation threshold
        recommendations = walk_path(A, D, F, src, rdd_graph_shell, 1)

USER_MOVIE_NETWORK_Gaussian.filter(lambda x: (x[0][0]=='2' and x[1][0][1]=='u') or (x[0][1]=='u' and x[1][0][0]=='2')).collect()

        #MOVIE_NETWORK2=sc.parallelize([((u'122', 'm'), ((u'376', 'm'), 0.47)), ((u'122', 'm'), ((u'185', 'm'), 0.456)), ((u'231', 'm'), 
        ((u'539', 'm'), 0.989)), ((u'185', 'm'), ((u'231', 'm'), 0.632)), ((u'231', 'm'), ((u'376', 'm'), 0.809)), ((u'122', 'm'), 
        ((u'539', 'm'), 0)), ((u'376', 'm'), ((u'539', 'm'), 0.503)), ((u'122', 'm'), ((u'231', 'm'), 0.574)), ((u'185', 'm'), 
        ((u'539', 'm'), 0.391)), ((u'185', 'm'), ((u'376', 'm'), 0.169)), ((u'376', 'm'), ((u'122', 'm'), 0.47)), ((u'185', 'm'), 
        ((u'122', 'm'), 0.456)), ((u'539', 'm'), ((u'231', 'm'), 0.989)), ((u'231', 'm'), ((u'185', 'm'), 0.632)), ((u'376', 'm'), 
        ((u'231', 'm'), 0.809)), ((u'539', 'm'), ((u'122', 'm'), 0)), ((u'539', 'm'), ((u'376', 'm'), 0.503)), 
        ((u'231', 'm'), ((u'122', 'm'), 0.574)), ((u'539', 'm'), ((u'185', 'm'), 0.391)), ((u'376', 'm'), ((u'185', 'm'), 0.169))])
