'''
Created on Nov 13, 2015

@author: lin
'''
import session
import itertools
import os
import subprocess
import codecs

class DataManip:
    def block_dat(self, dir, train_file, test_file, sep):
        def write_block(in_file, path, libfm_path, x_files, group_maps):
            file = open(in_file, "r")
            files = []
            for subpath in path:
                files.append(open(dir+subpath, "w"))
            libfm = open(dir + libfm_path, "w")
            
            for line in file:
                fields = line.rstrip().split(sep)
                for idx in range(len(fields)-1):
                    field, map, x_file, file = fields[idx], group_maps[idx], x_files[idx], files[idx]
                    value = 1
                    if field not in map:
                        map[field] = len(map)
                        x_file.write(str(map[field]) + ":" + str(value) + "\n")
                    file.write(str(map[field]) + "\n")
                libfm.write(fields[-1] + "\n")

        if not os.path.exists(dir + "/block/"):
            os.makedirs(dir + "/block/")

        user_map, video_map = {}, {}
        group_maps = [user_map, video_map]

        x_path = ["/block/fixed.x", "/block/sampled.x"]
        x_files = []
        for subpath in x_path:
            x_files.append(open(dir+subpath, "w"))

        # do train data
        train_path = ["/block/fixed.train", "/block/sampled.train"]
        write_block(train_file, train_path, "/block/train.libfm", x_files, group_maps)
            
        # do test data
        test_path = ["/block/fixed.test", "/block/sampled.test"]
        write_block(test_file, test_path, "/block/test.libfm", x_files, group_maps)
        
        # write the mapping
        u_mapfile = open(dir + "/block/user.map", "w")
        v_mapfile = open(dir + "/block/video.map", "w")
        for user in user_map:
            u_mapfile.write(str(user_map[user]) + " " + user + '\n')
        for video in video_map:
            v_mapfile.write(str(video_map[video]) + ' ' + video + '\n')
            

    def get_triple(self, dirpath, sep = ' '): 
        def make_dat_file(file, res):
            for idx in range(len(res)):
                delt = 0
                user, video, time = res[idx];
                file.write(user + sep + video + sep + time.strftime("%s") + "\n")

        s = session.MySession()
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
    
    def train_model(self, block_path):
        if not os.path.exists(block_path + "/output/"):
            os.makedirs(block_path + "/output/")
        libfm = block_path + "/libFM"
        command = libfm + " -task r -train " + block_path + "/train.libfm " +\
        "-test " + block_path + "/test.libfm -dim '1,1,100' -method bpr -relation " + block_path + "/fixed," + block_path + "/sampled -threads 4 -neg_sample 2 -out_conv " +\
        block_path + "/convergence.dat -top_k 4 -out_ranked_list_dir output -iter 100" 
        print command
        command_list = list(command)
        child = subprocess.Popen(command_list)
        child.wait()
    def map_real(self, block_path):
        
        test_map = {}
        s = session.MySession()
        res = s.get_test_user_videos()
        once = True
        # unicode
        for each in res:
            u, v = each[0].encode("utf-8"), each[1].encode("utf-8")
            if u not in test_map:
                test_map[u] = [v]
            else:
                test_map[u].append(v)
        print test_map
        
        out_path = block_path + "/real_output"
        if not os.path.exists(out_path):
            os.makedirs(out_path)
        
        filenames = []
        in_path = block_path + "/output"
        for _, _, fnames in os.walk(in_path):
            filenames = fnames
            
        umapf = open(block_path + "/user.map")
        vmapf = open(block_path + "/video.map")
        umap, vmap = {}, {}
        for line in umapf:
            id, r_id = line.split(' ')[0], line.split(' ')[1][:-1]
            umap[id] = r_id
        for line in vmapf:
            id, r_id = line.split(' ')[0], line.split(' ')[1][:-1]
            vmap[id] = r_id
        
        count = 0
        for name in filenames:
            in_file_path = in_path + "/" + name
            in_file = open(in_file_path, "r")
            user = name[:-4]
            r_user = umap[user]
            out_file_path = out_path + "/" + r_user 
            out_file = open(out_file_path, "w")
            out_file.write(r_user + '\n')
            for line in in_file:
                video, score = line.split("\t")[0], line.split("\t")[1]
                r_video = vmap[video]
#                 print type(r_user)
                if r_user in test_map and r_video in test_map[r_user]:
                    print r_user
                    count += 1
                    out_file.write(r_video + '\t' + score[:-1] + ' ***\n')
                else:
                    out_file.write(r_video + '\t' + score[:-1] + '\n')
            out_file.close()
            in_file.close()
        print "count: ", count

    def compare_result(self, block_path):        
        dirpath = block_path + "/real_output"
        real_videos, rec_videos = {}, {}
        s = session.MySession()
        filenames = []
        for _, _, fns in os.walk(dirpath):
            filenames = fns
        print filenames

        comp_dir = block_path + "/comp_output"
        if not os.path.exists(comp_dir):
            os.makedirs(comp_dir)

        for filename in filenames:
            user = filename
            in_file = open(dirpath + '/' + user, "r")
            in_file.readline()
            temp = []
            for line in in_file:
                video = line.split('\t')[0]
                temp.append(video)
                
            rec_videos[user] = []
            for id in temp:
                rec_videos[user].append(s.get_video_by_video(id))
            
            real_videos[user] = s.get_videos_by_user(user)
            l = len(real_videos[user])
            print user, l
            
            out_file = codecs.open(comp_dir + "/" + user, "w", encoding = 'utf8')
            for video in rec_videos[user]:
                if video in real_videos[user]:
                    video.id = video.id if video.id is not None else ""
                    video.title = video.title if video.title is not None else ""
                    video.category = video.category if video.category is not None else ""
                    out_file.write(video.id +  "\t" + video.title + '\t' + video.category + '\n')

            out_file.write('\n\n')

            for video in rec_videos[user]:
                
                video.id = video.id if video.id is not None else ""
                video.title = video.title if video.title is not None else ""
                video.category = video.category if video.category is not None else ""
                out_file.write(video.id +  "\t" + video.title + '\t' + video.category + '\n')
                
            out_file.write('\n\n')
            l = len(real_videos[user])
            out_file.write(str(l) + '\n')
            for video in real_videos[user]:
                video.id = video.id if video.id is not None else ""
                video.title = video.title if video.title is not None else ""
                video.category = video.category if video.category is not None else ""
                out_file.write(video.id +  "\t" + video.title + '\t' + video.category + '\n')
                
    def make_title(self):
        dir = '/home/lin/workspace/data/youku'
        file = codecs.open(dir + "/ctrain.dat", encoding = 'utf8')
        out = codecs.open(dir + '/ctrain.out', 'w', encoding = 'utf8')
        s = session.MySession()
        idx = 1
        for line in file:
            line.strip()
            u, v1, v2, delta = line.split(' ')
            v1 = s.get_video_by_video(v1)
            v2 = s.get_video_by_video(v2)
            v1.title = "None" if v1.title is None else v1.title
            v2.title = "None" if v2.title is None else v2.title
            out.write(u + "\n" + v1.title + "\n" + v2.title + '\n' + delta + '\n')
            idx += 1

            
    
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
                    video = line.split('\t')[0].rstrip()
                    rec_user_video[uname].append(video)
        
        # true list
        test_user_video = {}
        for user, video in itertools.izip(fixed_test, sampled_test):
            user, video = user.rstrip(), video.rstrip()
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

            for user in rec_user_video:
                if user not in test_user_video: continue
                if len(rec_user_video[user]) == 0: continue

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
            print "sum of users: ", sum_of_users
            print "precision: ", sum_of_precision / sum_of_users
            print "recall: ", sum_of_recall / sum_of_users
            print "map: ", sum_of_ave_precision / sum_of_users
            print "hit_user: ", len(user_list)
                
          
    def exesql(self, query):
        import MySQLdb
        
        db = MySQLdb.connect(host='localhost', port = 3306, user='root', passwd='123456', db = 'new_vod', charset='utf8', use_unicode=True)
        cursor = db.cursor()
        
#         print query
        cursor.execute(query)
        
        return cursor
    
    def print_v_list(self, vl, file = None):    
        query = ("select title from video where id in %s")
        str = '('
        for each in vl:
            str += "'"
            str += each
            str += "',"
        str = str[:-1] + ')'
        query = query % str
        cursor = dm.exesql(query)
        for title, in cursor:
            if title is None: title = '???????????????????'
            if file is None: print title
            else: file.write(title + '\n')
        cursor.close()

    def pred_vs_real(self,path):
        res = []
        for _, _, filenames in os.walk(path):
            for filename in filenames:
                file = open(path + '/' + filename, 'r')
                pred, real = [], []
                cnt = 5
                for line in file:
                    line = line.rstrip()
                    v = line.split(' ')[0]
                    if cnt != 0:
                        pred.append(v)
                        cnt -= 0
                    if line[-1] == '*':
                        real.append(v)
                res.append((pred,real))
        return res 

if __name__ == "__main__":
    dm = DataManip()
#     dirpath = "/home/lin/workspace/data/youku"
    dirpath = "/home/lin/workspace/data/youtube"
#     dirpath = "/home/lin/workspace/data/ml-100k"
    block_path = dirpath + "/block"
    train = dirpath + "/train.dat"
    test = dirpath + "/test.dat"
#     train = dirpath + "/u1.base"
#     test = dirpath + "/u1.test"
    sep = ","
    dm.get_triple(dirpath, sep)
#     dm.block_dat(dirpath, train, test, sep)
#    do the training!!!!!!!!!!!!!!!
#     dm.cal_prec(block_path)

#     pred_real = dm.pred_vs_real(block_path+"/output")
#     file = codecs.open(block_path + "/pred_vs_real.out", 'w+', encoding = 'utf8')
#     cnt = 0
#     for pred, real in pred_real:
#         print cnt 
#         cnt += 1
#         file.write('start...\n')
#         dm.print_v_list(pred, file)
#         file.write('\n')
#         dm.print_v_list(real, file)
#         file.write('---------------------------------------\n')
        





































