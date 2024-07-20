import numpy as np
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from contact_graspnet.contact_graspnet.grasp import *
from contact_graspnet.contact_graspnet.my_grasp_api import generate_grasp
import subprocess

def kmeans_without_n(data):
    # 确定最佳聚类数量
    silhouette_scores = []
    k_range = range(2, 11)  # 通常从2到10或更多

    for k in k_range:
        kmeans = KMeans(n_clusters=k, random_state=42)
        kmeans.fit(data)
        score = silhouette_score(data, kmeans.labels_)
        silhouette_scores.append(score)

    # 找到轮廓系数最高的聚类数量
    best_k = k_range[np.argmax(silhouette_scores)]

    # 用最佳聚类数量进行 K-means 聚类
    kmeans = KMeans(n_clusters=best_k, random_state=42)
    kmeans.fit(data)
    labels = kmeans.labels_
    centroids = kmeans.cluster_centers_

    # according to labels seperate these grasps into different clusters and create a list of grasps in each cluster
    clusters=[]
    for i in range(best_k):
        cluster=[]
        clusters.append(cluster)
    for i in range(len(labels)):
        clusters[labels[i]].append(data[i])
    if len(clusters) == best_k:
        return best_k, clusters, labels
    else:
        return 0,0


def generate_colors(number, labels):
    # number: number of colors
    # labels: labels of each point

    start_color = (0, 0, 100)
    end_color = (120, 120, 255)
    
    

    base_colors = []
    colors = []
    for i in range(number+1):
        t = i /( number+1)
        r = (start_color[0] + t * (end_color[0] - start_color[0]))/255
        g = (start_color[1] + t * (end_color[1] - start_color[1]))/255
        b = (start_color[2] + t * (end_color[2] - start_color[2]))/255
        base_colors.append((r,g,b))
    for i in range(len(labels)):
            colors.append(base_colors[labels[i]])
    return colors, base_colors
    
def get_closest(points, point_cloud):
    
    points = np.array(points)
    point_cloud = np.array(point_cloud)
    # 计算距离矩阵
    distances = np.linalg.norm(points[:, np.newaxis, :] - point_cloud[np.newaxis, :, :], axis=2)

    # 找到距离最小的点的索引
    closest_points_indices = np.argmin(distances, axis=1)

    # 找到距离最小的点的坐标
    closest_points = point_cloud[closest_points_indices]

    # print(closest_points_indices)  # 打印最近点的索引
    # print(closest_points)          # 打印最近点的坐标
    return closest_points_indices

if __name__ == '__main__':

    pc_path = '/home/mlx/GraspTTA/models/HO3D_Object_models/035_power_drill/resampled.npy'
    grasp_path='/home/mlx/handover_ws/grasp_data/grasps.npz'
    # pointcloud, Ts = generate_grasp(pc_path)
    # np.savez('/home/mlx/handover_ws/grasp_data/grasps.npz', grasp = Ts)

    # cmd = subprocess.run(['python', 'contact_graspnet/contact_graspnet/my_grasp_api.py', '--pointcloud_path', pc_path, '--output_path', grasp_path])

    # print(cmd.stdout)

    pointcloud = np.load(pc_path)
    angle = np.pi
    R = np.array([[1,0,0],[0,np.cos(angle), -np.sin(angle)],[0,np.sin(angle), np.cos(angle)]])
    pointcloud= np.dot(pointcloud, R.T)

    file = np.load(grasp_path)
    grasp_list = file['grasp']
    print(len(grasp_list))
    # grasp_list = Ts

    data = grasp_list.reshape((200, 16))
    print(len(data))
    # data = data[:, 0 : 12]
    
    indices = [3,7,11]
    data = [[row[i] for i in indices] for row in data]
    # print(len(data))
    # print(len(data[0]))
    
    closest_pc = get_closest(data, pointcloud)

        
    
    num_clusters, clusters, labels = kmeans_without_n(data)
    print(num_clusters)
    # print(type(clusters[0][0]))
    # print(clusters[0][0])
    
    colors, base_colors = generate_colors(num_clusters, labels)
    print(base_colors)
    print(len(colors))
    
    # draw_scene(pointcloud, grasps_list, grasp_colors=colors, save_dir='/home/mlx/handover_ws/cluster/test.png')
    draw_scene(pointcloud, grasp_list, grasp_colors=colors)
    


    # 可视化轮廓系数
    # plt.plot(k_range, silhouette_scores, marker='o')
    # plt.xlabel('Number of clusters')
    # plt.ylabel('Silhouette Score')
    # plt.title('Silhouette Scores for different numbers of clusters')
    # plt.show()

    # 使用 PCA 将数据降至2维，以便于可视化
    # pca = PCA(n_components=2)
    # reduced_data = pca.fit_transform(data)

    # # 可视化聚类结果
    # plt.scatter(reduced_data[:, 0], reduced_data[:, 1], c=labels, cmap='viridis', marker='o')
    # plt.scatter(pca.transform(centroids)[:, 0], pca.transform(centroids)[:, 1], c='red', marker='x')
    # plt.title(f"K-means Clustering with PCA (Best k={best_k})")
    # plt.xlabel("Principal Component 1")
    # plt.ylabel("Principal Component 2")
    # plt.show()