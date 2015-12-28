'''
Created on Nov 13, 2015

@author: lin
'''
import db_session
import itertools
import os
import subprocess
import codecs

class DataManip:
    def block_dat(self, dir, train_file, test_file, sep):
        if not os.path.exists(dir + "/block/"):
            os.makedirs(dir + "/block/")

        # do train data
        file = open(train_file, "r")
        fixed_train = open(dir + "/block/fixed.train", "w")
        sampled_train = open(dir + "/block/sampled.train", "w")
        train_libfm = open(dir + "/block/train.libfm", "w")
    
        userIdx, videoIdx = 0, 0
        user_map, video_map = {}, {}
        for line in file:
            user, video = line.split(sep)[0], line.split(sep)[1]
            if user not in user_map:
                user_map[user] = userIdx
                userIdx += 1
            if video not in video_map:
                video_map[video] = videoIdx
                videoIdx += 1
            fixed_train.write(str(user_map[user]) + "\n")
            sampled_train.write(str(video_map[video]) + "\n")
            train_libfm.write("1\n")
            
        # do test data
        file = open(test_file, "r")
        fixed_test = open(dir + "/block/fixed.test", "w")
        sampled_test = open(dir + "/block/sampled.test", "w")
        test_libfm = open(dir + "/block/test.libfm", "w")
    
        for line in file:
            user, video = line.split(sep)[0], line.split(sep)[1]
            if user not in user_map:
                user_map[user] = userIdx
                userIdx += 1
            if video not in video_map:
                video_map[video] = videoIdx
                videoIdx += 1
            fixed_test.write(str(user_map[user]) + "\n")
            sampled_test.write(str(video_map[video]) + "\n")
            test_libfm.write("0\n")
    
        fixed_x = open(dir + "/block/fixed.x", "w")
        for i in range(userIdx):
            fixed_x.write(str(i) + ":" + "1\n")
    
        sampled_x = open(dir + "/block/sampled.x", "w")
        for i in range(videoIdx):
            sampled_x.write(str(i) + ":" + "1\n")
            
        # write the mapping
        u_mapfile = open(dir + "/block/user.map", "w")
        v_mapfile = open(dir + "/block/video.map", "w")
        for user in user_map:
            u_mapfile.write(str(user_map[user]) + sep + user + '\n')
        for video in video_map:
            v_mapfile.write(str(video_map[video]) + sep + video + '\n')

    def get_triple(self, dirpath, sep = ' '): 
        def make_dat_file(file, res):
            for idx in range(len(res)):
                delt = 0
                user, video, time = res[idx];
                file.write(user + sep + video + sep + time.strftime("%s") + "\n")
 
        s = db_session.DbSession()
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)
         
        res = s.get_data("train")
        file = codecs.open(dirpath + "/train.dat", "w", encoding='utf8')
        make_dat_file(file, res)
        file.close()        
         
        res = s.get_data("test")
        file = codecs.open(dirpath + "/test.dat", "w", encoding='utf8')
        make_dat_file(file, res)
        file.close() 

    

                
    def cal_prec(self, block_path):
        # load the mapping
        umapf = open(block_path + '/user.map', 'r')
        vmapf = open(block_path + '/video.map', 'r')
        umap, vmap = {}, {}
        
        for line in umapf:
            i, u = line.split(' ')[0], line.split(' ')[1]
            umap[i] = u
        for line in vmapf:
            i, v = line.split(' ')[0], line.split(' ')[1]
            vmap[i] = v
        
        
        fixed_test = file(block_path + "/fixed.test", "r")
        sampled_test = file(block_path + "/sampled.test", "r")
        fixed_x = file(block_path + "/fixed.x", "r")
        
        # recommend list
        rec_user_video = {}
        for line in fixed_x:
            user = line.split(":")[0]
            rec_user_video[user] = []
        print "len of user: ", len(rec_user_video)  
  
            
        rank_list_dir = block_path + "/output"
        for _, _, filenames in os.walk(rank_list_dir):
            for filename in filenames:
                filepath = rank_list_dir + "/" + filename
                uname = filename[:-4]
                rank_list = open(filepath, "r")
                for line in rank_list:
                    video = line.split('\t')[0]
                    rec_user_video[uname].append(video)
        
        # true list
        test_user_video = {}
        for user, video in itertools.izip(fixed_test, sampled_test):
            user, video = user[:-1], video[:-1]
            if user not in test_user_video:
                test_user_video[user] = [video]
            else:
                test_user_video[user].append(video)
        
        for K in range(1,21):

            sum_of_precision = 0.0
            sum_of_recall = 0.0
            sum_of_ave_precision = 0.0
            sum_of_users = 0.0
            user_list = []

            count = 0
            for user in rec_user_video:
                count += 1
                if user not in test_user_video: 
                    continue
                if len(rec_user_video[user]) == 0: 
                    continue

                test_video_len = len(test_user_video[user])              
                denominator = min(K, test_video_len)
                cul_denom = 0.0
                hit = 0.0
                ap = 0.0
                has_one = False

                for video in rec_user_video[user][:denominator]:
                    cul_denom += 1.0
                    if video in test_user_video[user]:
                        has_one = True
                        hit += 1.0
                        ap += hit/cul_denom * 1/denominator
                
                sum_of_recall += hit/test_video_len
                sum_of_precision += hit/denominator
                sum_of_ave_precision += ap
                sum_of_users += 1.0
                if has_one: user_list.append(umap[user][:-1])
            
            print "K: ", K
            print "count: ", count
            print "sum of users: ", sum_of_users
            print "precision: ", sum_of_precision / sum_of_users
            print "recall: ", sum_of_recall / sum_of_users
            print "map: ", sum_of_ave_precision / sum_of_users
            print "hit_user: ", user_list
                
    def avg_interval(self, path, sep):
        file = codecs.open(path, 'r', encoding = 'utf8')       
        avg = []
        cum = 0.
        cnt = 0
        preu = ''
        pret = 0
        for line in file:
            line = line.rstrip()
            u, v, t = line.split(sep)
            t = int(t)
            if u != preu:
                if cnt == 0: pass
                else: 
                    avg.append(cum/cnt)
                cum = 0.
                cnt = 0
                preu = u
                pret = t
                continue
            
            if t-pret <= 3600:
                cum += (t-pret)
                cnt += 1
                pret = t
        
#         print avg
        import matplotlib.pyplot as plt
        plt.hist(avg, bins=200)
        plt.show()
            
            
            
        
    


if __name__ == "__main__":
    dm = DataManip()
#     dirpath = "/home/lin/workspace/data/youku"
    dirpath = "/home/lin/workspace/data/youtube"
#     dirpath = "/home/lin/workspace/data/ml-10M100K/"
    block_path = dirpath + "/block"
    train = dirpath + "/train.dat"
    test = dirpath + "/test.dat"
    sep = "\t"
#     dm.get_triple(dirpath,sep)
    dm.avg_interval(train,sep)

#     dm.block_dat(dirpath, train, test, sep)
#    do the training!!!!!!!!!!!!!!!
#     dm.cal_prec(block_path)






































