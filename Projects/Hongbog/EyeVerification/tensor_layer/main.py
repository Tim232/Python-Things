import time
from collections import Counter
import numpy as np
import tensorflow as tf
import os
from PIL import Image
import cv2
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

from Hongbog.EyeVerification.tensor_layer.model_v1 import Model
from Hongbog.EyeVerification.common.dataloader import DataLoader

class Neuralnet:
    '''하이퍼파라미터 관련 변수'''
    _FLAGS = None

    '''훈련시 필요한 변수'''
    _model = None
    _saver = None
    _best_model_params = None

    def __init__(self, is_train, save_type=None):
        self.is_train = is_train
        self.save_type = save_type
        self._flag_setting()  # flag setting

        if (self.is_train == True) and (save_type == 'db'):  # data loading
            # self.db = Database(FLAGS=self._FLAGS, train_log=1)
            # self.db.init_database()
            self.loader = DataLoader(batch_size=self._FLAGS.batch_size, train_right_root_path=self._FLAGS.train_right_root_path, test_right_root_path=self._FLAGS.test_right_root_path,
                                     train_left_root_path=self._FLAGS.train_left_root_path, test_left_root_path=self._FLAGS.test_left_root_path)

    def _flag_setting(self):
        '''
        하이퍼파라미터 값을 설정하는 함수
        :return: None
        '''
        flags = tf.app.flags
        self._FLAGS = flags.FLAGS
        flags.DEFINE_string('train_right_root_path', 'D:\\100_dataset\\eye_verification\\eye_only_v2\\train\\right', '오른쪽 눈 학습 데이터 경로')
        flags.DEFINE_string('test_right_root_path', 'D:\\100_dataset\\eye_verification\\eye_only_v2\\test\\right', '오른쪽 눈 테스트 데이터 경로')
        flags.DEFINE_string('train_left_root_path', 'D:\\100_dataset\\eye_verification\\eye_only_v2\\train\\left', '왼쪽 눈 학습 데이터 경로')
        flags.DEFINE_string('test_left_root_path', 'D:\\100_dataset\\eye_verification\\eye_only_v2\\test\\left', '왼쪽 눈 테스트 데이터 경로')
        flags.DEFINE_integer('epochs', 120, '훈련시 에폭 수')
        flags.DEFINE_integer('batch_size', 50, '훈련시 배치 크기')
        flags.DEFINE_integer('max_checks_without_progress', 20, '특정 횟수 만큼 조건이 만족하지 않은 경우(Early Stop Condition)')
        flags.DEFINE_string('trained_param_path',
                            'D:/05_source/PythonRepository/Hongbog/EyeVerification/train_log/1th_test',
                            '훈련된 파라미터 값 저장 경로')
        self.config = tf.ConfigProto(
            gpu_options=tf.GPUOptions(allow_growth=True, per_process_gpu_memory_fraction=1)
        )

    def train(self):
        train_num = self.loader.train_right_x_len // self._FLAGS.batch_size
        test_num = self.loader.test_right_x_len // self._FLAGS.batch_size
        train_right_batch1, train_right_batch2, train_right_batch3, train_right_batch4, train_right_batch5, train_right_batch6,\
        train_left_batch1, train_left_batch2, train_left_batch3, train_left_batch4, train_left_batch5, train_left_batch6 = self.loader.train_loader()
        test_right_batch, test_left_batch = self.loader.test_loader()

        with tf.Session(config=self.config) as sess:
            right_model = Model(sess=sess, name='right', training=self.is_train)
            left_model = Model(sess=sess, name='left', training=self.is_train)

            print('>> Tensorflow session built. Variables initialized.')
            sess.run(tf.global_variables_initializer())

            self._saver = tf.train.Saver()

            # ckpt_st = tf.train.get_checkpoint_state(os.path.join(self._FLAGS.trained_param_path, '000001'))

            # if ckpt_st is not None:
            #     self._saver.restore(sess, ckpt_st.model_checkpoint_path)
            #     print('>> Model Restored')

            coord = tf.train.Coordinator()
            threads = tf.train.start_queue_runners(sess=sess, coord=coord)
            print('>> Running started.')

            epoch = 1

            for epoch in range(1, self._FLAGS.epochs+1):
                tot_train_right_acc, tot_train_right_loss = [], []
                tot_train_left_acc, tot_train_left_loss = [], []
                tot_test_right_acc, tot_test_right_loss = [],[]
                tot_test_left_acc, tot_test_left_loss = [], []

                if epoch % 50 == 0:
                    right_model.learning_rate /= 2
                    left_model.learning_rate /= 2

                train_st = time.time()
                for step in range(1, train_num+1):
                    '''Data Loading - (right, left 300 개씩)'''
                    right_train_data_01, right_train_data_02, right_train_data_03, right_train_data_04, right_train_data_05, right_train_data_06,\
                    left_train_data_01, left_train_data_02, left_train_data_03, left_train_data_04, left_train_data_05, left_train_data_06 = sess.run([train_right_batch1, train_right_batch2, train_right_batch3, train_right_batch4, train_right_batch5, train_right_batch6,
                                                                                                                                                       train_left_batch1, train_left_batch2, train_left_batch3, train_left_batch4, train_left_batch5, train_left_batch6])
                    train_right_batch_x = np.concatenate([right_train_data_01[0], right_train_data_02[0], right_train_data_03[0], right_train_data_04[0], right_train_data_05[0], right_train_data_06[0]])
                    train_right_batch_y = np.concatenate([right_train_data_01[1], right_train_data_02[1], right_train_data_03[1], right_train_data_04[1], right_train_data_05[1], right_train_data_06[1]])
                    train_left_batch_x = np.concatenate([left_train_data_01[0], left_train_data_02[0], left_train_data_03[0], left_train_data_04[0], left_train_data_05[0], left_train_data_06[0]])
                    train_left_batch_y = np.concatenate([left_train_data_01[1], left_train_data_02[1], left_train_data_03[1], left_train_data_04[1], left_train_data_05[1], left_train_data_06[1]])

                    '''Model Train'''
                    st = time.time()
                    step_train_right_acc, step_train_right_loss = [], []
                    for idx in range(0, 300, self._FLAGS.batch_size):
                        train_right_acc, train_right_loss, _ = right_model.train(train_right_batch_x[idx:idx+self._FLAGS.batch_size], train_right_batch_y[idx:idx+self._FLAGS.batch_size])
                        step_train_right_acc.append(train_right_acc)
                        step_train_right_loss.append(train_right_loss)
                        tot_train_right_acc.append(train_right_acc)
                        tot_train_right_loss.append(train_right_loss)

                    step_train_left_acc, step_train_left_loss = [], []
                    for idx in range(0, 300, self._FLAGS.batch_size):
                        train_left_acc, train_left_loss, _ = left_model.train(train_left_batch_x[idx:idx+self._FLAGS.batch_size], train_left_batch_y[idx:idx+self._FLAGS.batch_size])
                        step_train_left_acc.append(train_left_acc)
                        step_train_left_loss.append(train_left_loss)
                        tot_train_left_acc.append(train_left_acc)
                        tot_train_left_loss.append(train_left_loss)
                    et = time.time()

                    step_train_right_acc = float(np.mean(np.array(step_train_right_acc)))
                    step_train_right_loss = float(np.mean(np.array(step_train_right_loss)))
                    step_train_left_acc = float(np.mean(np.array(step_train_left_acc)))
                    step_train_left_loss = float(np.mean(np.array(step_train_left_loss)))
                    print(">> [Step-Train] epoch/step: [%d/%d], [Right]Accuracy: %.6f, [Left]Accuracy: %.6f, [Right]Loss: %.6f, [Left]Loss: %.6f, step_time: %.2f"
                          % (epoch, step, step_train_right_acc, step_train_left_acc, step_train_right_loss, step_train_left_loss, et - st))
                train_et = time.time()
                tot_train_time = train_et - train_st

                '''Model Test'''
                right_prob, right_label = [], []
                left_prob, left_label = [], []
                ensemble_prob, ensemble_label = [], []
                tot_ensemble_acc = []

                for step in range(1, test_num + 1):
                    right_test_data_01, left_test_data_01 = sess.run([test_right_batch, test_left_batch])
                    test_right_batch_x, test_right_batch_y = right_test_data_01
                    test_left_batch_x, test_left_batch_y = left_test_data_01

                    test_right_acc, test_right_loss, test_right_prob = right_model.validation(test_right_batch_x, test_right_batch_y)
                    test_left_acc, test_left_loss, test_left_prob = left_model.validation(test_left_batch_x, test_left_batch_y)

                    '''Ensemble Prediction'''
                    tot_ensemble_acc.append(np.sum(np.argmax(test_right_prob + test_left_prob, axis=1) == np.array(test_right_batch_y)) / self._FLAGS.batch_size)

                    '''Monitoring'''
                    tot_test_right_acc.append(test_right_acc)
                    tot_test_right_loss.append(test_right_loss)
                    tot_test_left_acc.append(test_left_acc)
                    tot_test_left_loss.append(test_left_loss)

                    '''Confusion Matrix'''
                    right_prob.append(np.argmax(test_right_prob, axis=1).flatten().tolist())
                    right_label.append(test_right_batch_y.flatten().tolist())
                    left_prob.append(np.argmax(test_left_prob, axis=1).flatten().tolist())
                    left_label.append(test_left_batch_y.flatten().tolist())
                    ensemble_prob.append(np.argmax(test_right_prob + test_left_prob, axis=1).flatten().tolist())
                    ensemble_label.append(test_right_batch_y.flatten().tolist())

                tot_train_right_acc = float(np.mean(np.array(tot_train_right_acc)))
                tot_train_right_loss = float(np.mean(np.array(tot_train_right_loss)))
                tot_train_left_acc = float(np.mean(np.array(tot_train_left_acc)))
                tot_train_left_loss = float(np.mean(np.array(tot_train_left_loss)))

                tot_test_right_acc = float(np.mean(np.array(tot_test_right_acc)))
                tot_test_right_loss = float(np.mean(np.array(tot_test_right_loss)))
                tot_test_left_acc = float(np.mean(np.array(tot_test_left_acc)))
                tot_test_left_loss = float(np.mean(np.array(tot_test_left_loss)))
                tot_ensemble_acc = float(np.mean(np.array(tot_ensemble_acc)))

                print('>> [Total-Train] epoch: [%d], [Right]Accuracy: %.6f, [Left]Accuracy: %.6f, [Right]Loss: %.6f, [Left]Loss: %.6f, time: %.2f'
                      % (epoch, tot_train_right_acc, tot_train_left_acc, tot_train_right_loss, tot_train_left_loss, tot_train_time))
                print('>> [Total-Test] epoch: [%d], [Right]Accuracy: %.6f, [Left]Accuracy: %.6f, [Ensemble]Accuracy: %.6f, [Right]Loss: %.6f, [Left]Loss: %.6f'
                    % (epoch, tot_test_right_acc, tot_test_left_acc, tot_ensemble_acc, tot_test_right_loss, tot_test_left_loss))
                print('>> [Right-Confusion-Matrix]')
                print(sess.run(tf.confusion_matrix(labels=np.array(right_label).flatten(),
                                                   predictions=np.array(right_prob).flatten(), num_classes=7)))
                print('>> [Left-Confusion-Matrix]')
                print(sess.run(tf.confusion_matrix(labels=np.array(left_label).flatten(), predictions=np.array(left_prob).flatten(), num_classes=7)))
                print('>> [Ensemble-Confusion-Matrix]')
                print(sess.run(tf.confusion_matrix(labels=np.array(ensemble_label).flatten(), predictions=np.array(ensemble_prob).flatten(), num_classes=7)))

                # self.db.mon_data_to_db(epoch, tot_train_acc, tot_test_acc, tot_train_loss, tot_test_loss, tot_train_time, tot_test_time)

                # kernel = tf.get_collection(tf.GraphKeys.GLOBAL_VARIABLES, 'right/output_layer/logit/W_conv2d')[0]
                # print(sess.run(kernel))

                ## Save model
                os.makedirs(os.path.join(self._FLAGS.trained_param_path), exist_ok=True)
                self._saver.save(sess, os.path.join(self._FLAGS.trained_param_path, 'eye_verification_param'), global_step=epoch)
                print('>> [Model saved] epoch: %d' % (epoch))

            coord.request_stop()
            coord.join(threads)

            # self.db.close_conn()

    def cam_test(self):
        sample_num = 3  # 클래스 당 테스트 샘플 개수
        class_num = 7  # 전체 클래스 개수
        batch_size = 3 * 7
        img_size = (100, 50)
        right_sample_path = 'D:\\100_dataset\\eye_verification\\eye_only_v2\\test\\right'
        left_sample_path = 'D:\\100_dataset\\eye_verification\\eye_only_v2\\test\\left'

        def save_matplot_img(right_outputs, left_outputs, sample_num, class_num):
            f = plt.figure(figsize=(10, 8))
            outer = gridspec.GridSpec(1, 2, wspace=0.2, hspace=0.2)
            right_inner = gridspec.GridSpecFromSubplotSpec(7, 3, subplot_spec=outer[0], wspace=0.1, hspace=0.1)
            left_inner = gridspec.GridSpecFromSubplotSpec(7, 3, subplot_spec=outer[1], wspace=0.1, hspace=0.1)

            for cls in range(class_num):
                for sample in range(sample_num):
                    subplot = plt.Subplot(f, right_inner[sample + cls * sample_num])
                    subplot.imshow(right_outputs[sample + cls * sample_num])
                    f.add_subplot(subplot)

                    subplot = plt.Subplot(f, left_inner[sample + cls * sample_num])
                    subplot.imshow(left_outputs[sample + cls * sample_num])
                    f.add_subplot(subplot)

            f.savefig('D:\\grad_cam\\cam_test.png')
            print('>> Grad CAM Complete')

        def get_file_names():
            right_file_names, left_file_names = [], []

            for cls in range(class_num):
                right_file_name = [[os.path.join(path, file) for file in files] for path, dir, files in os.walk(os.path.join(right_sample_path, str(cls)))]
                right_file_name = np.array(right_file_name).flatten()

                left_file_name = [[os.path.join(path, file) for file in files] for path, dir, files in os.walk(os.path.join(left_sample_path, str(cls)))]
                left_file_name = np.array(left_file_name).flatten()

                random_sort = np.random.permutation(right_file_name.shape[0])
                right_file_name = right_file_name[random_sort][:sample_num]
                left_file_name = left_file_name[random_sort][:sample_num]

                for r_file_name, l_file_name in zip(right_file_name, left_file_name):
                    right_file_names.append(r_file_name)
                    left_file_names.append(l_file_name)

            right_file_names = tf.convert_to_tensor(right_file_names, dtype=tf.string)
            left_file_names = tf.convert_to_tensor(left_file_names, dtype=tf.string)

            return right_file_names, left_file_names

        def data_preprocessing(path):
            with tf.variable_scope('data_preprocessing'):
                data = tf.read_file(path)
                data = tf.image.decode_png(data, channels=1, name='decode_img')
                data = tf.image.resize_images(data, size=img_size)
                data = tf.divide(data, 255.)
            return data

        def data_loader(right_file_names, left_file_names):
            with tf.variable_scope('data_loader'):
                # 데이터셋을 불러오는데 불러오는 데이터는 텐서타입이어서 배치단위로 계속 부르기 위해 텐서슬라이스 함수를 반복적으로 사용한다.
                right_dataset = tf.contrib.data.Dataset.from_tensor_slices(right_file_names).repeat()
                left_dataset = tf.contrib.data.Dataset.from_tensor_slices(left_file_names).repeat()

                right_normal_dataset_map = right_dataset.map(data_preprocessing).batch(batch_size)
                right_normal_iterator = right_normal_dataset_map.make_one_shot_iterator()
                right_normal_batch_input = right_normal_iterator.get_next()

                left_normal_dataset_map = left_dataset.map(data_preprocessing).batch(batch_size)
                left_normal_iterator = left_normal_dataset_map.make_one_shot_iterator()
                left_normal_batch_input = left_normal_iterator.get_next()

            return right_normal_batch_input, left_normal_batch_input

        right_file_names, left_file_names = get_file_names()
        right_batch_img, left_batch_img = data_loader(right_file_names, left_file_names)

        with tf.Session() as sess:
            right_model = Model(sess=sess, name='right', training=self.is_train)
            left_model = Model(sess=sess, name='left', training=self.is_train)

            self._saver = tf.train.Saver()
            ckpt_st = tf.train.get_checkpoint_state(os.path.join(self._FLAGS.trained_param_path))

            if ckpt_st is not None:
                '''restore 시에는 tf.global_variables_initializer() 가 필요 없다.'''
                self._saver.restore(sess, ckpt_st.model_checkpoint_path)
                print('>> Model Restored')

            right_batch_x, left_batch_x = sess.run([right_batch_img, left_batch_img])
            right_file_names, left_file_names = sess.run([right_file_names, left_file_names])

            right_grad_cam = right_model.grad_cam(right_batch_x, sample_num * class_num)
            left_grad_cam = left_model.grad_cam(left_batch_x, sample_num * class_num)

            # 원본 영상과 Grad CAM 을 합친 결과
            right_outputs = []
            left_outputs = []

            for idx in range(sample_num * class_num):
                # 오른쪽 눈
                right_img = Image.open(right_file_names[idx], mode='r').convert('RGB')
                right_img = np.array(right_img.resize(img_size))
                right_img = right_img.astype(float)
                right_img /= 255.

                right_cam = cv2.applyColorMap(np.uint8(255 * right_grad_cam[idx]), cv2.COLORMAP_JET)
                right_cam = cv2.cvtColor(right_cam, cv2.COLOR_BGR2RGB)

                # grad-cam과 원본 이미지 중첩.
                alpha = 0.0025  # COLORMAP_JET 의 비율 값.
                right_output = right_img + alpha * right_cam
                right_output /= right_output.max()

                # 왼쪽 눈
                left_img = Image.open(left_file_names[idx], mode='r').convert('RGB')
                left_img = np.array(left_img.resize(img_size))
                left_img = left_img.astype(float)
                left_img /= 255.

                left_cam = cv2.applyColorMap(np.uint8(255 * left_grad_cam[idx]), cv2.COLORMAP_JET)
                left_cam = cv2.cvtColor(left_cam, cv2.COLOR_BGR2RGB)

                # grad-cam과 원본 이미지 중첩.
                alpha = 0.0025  # COLORMAP_JET 의 비율 값.
                left_output = left_img + alpha * left_cam
                left_output /= left_output.max()

                right_outputs.append(right_output)
                left_outputs.append(left_output)

            save_matplot_img(right_outputs, left_outputs, sample_num, class_num)

    def test(self):
        batch_size = 50
        img_size = (100, 50)
        right_sample_path = 'D:\\100_dataset\\eye_verification\\eye_only_v3\\test\\right\\0'
        left_sample_path = 'D:\\100_dataset\\eye_verification\\eye_only_v3\\test\\left\\0'

        def get_file_names():
            right_file_names, left_file_names = [], []

            right_file_name = [[os.path.join(path, file) for file in files] for path, dir, files in os.walk(right_sample_path)]
            right_file_name = np.array(right_file_name).flatten()

            left_file_name = [[os.path.join(path, file) for file in files] for path, dir, files in os.walk(left_sample_path)]
            left_file_name = np.array(left_file_name).flatten()

            random_sort = np.random.permutation(right_file_name.shape[0])
            right_file_name = right_file_name[random_sort]
            left_file_name = left_file_name[random_sort]

            for r_file_name, l_file_name in zip(right_file_name, left_file_name):
                right_file_names.append(r_file_name)
                left_file_names.append(l_file_name)

            right_file_names = tf.convert_to_tensor(right_file_names, dtype=tf.string)
            left_file_names = tf.convert_to_tensor(left_file_names, dtype=tf.string)

            return right_file_names, left_file_names

        def data_preprocessing(path):
            with tf.variable_scope('data_preprocessing'):
                data = tf.read_file(path)
                data = tf.image.decode_png(data, channels=1, name='decode_img')
                data = tf.image.resize_images(data, size=img_size)
                data = tf.divide(data, 255.)
            return data

        def data_loader(right_file_names, left_file_names):
            with tf.variable_scope('data_loader'):
                # 데이터셋을 불러오는데 불러오는 데이터는 텐서타입이어서 배치단위로 계속 부르기 위해 텐서슬라이스 함수를 반복적으로 사용한다.
                right_dataset = tf.contrib.data.Dataset.from_tensor_slices(right_file_names).repeat()
                left_dataset = tf.contrib.data.Dataset.from_tensor_slices(left_file_names).repeat()

                right_normal_dataset_map = right_dataset.map(data_preprocessing).batch(batch_size)
                right_normal_iterator = right_normal_dataset_map.make_one_shot_iterator()
                right_normal_batch_input = right_normal_iterator.get_next()

                left_normal_dataset_map = left_dataset.map(data_preprocessing).batch(batch_size)
                left_normal_iterator = left_normal_dataset_map.make_one_shot_iterator()
                left_normal_batch_input = left_normal_iterator.get_next()

            return right_normal_batch_input, left_normal_batch_input

        right_file_names, left_file_names = get_file_names()
        right_batch_img, left_batch_img = data_loader(right_file_names, left_file_names)

        with tf.Session() as sess:
            right_model = Model(sess=sess, name='right', training=self.is_train)
            left_model = Model(sess=sess, name='left', training=self.is_train)

            self._saver = tf.train.Saver()
            ckpt_st = tf.train.get_checkpoint_state(os.path.join(self._FLAGS.trained_param_path))

            if ckpt_st is not None:
                '''restore 시에는 tf.global_variables_initializer() 가 필요 없다.'''
                print(ckpt_st.model_checkpoint_path)
                self._saver.restore(sess, ckpt_st.model_checkpoint_path)
                print('>> Model Restored')

            # kernel = tf.get_collection(tf.GraphKeys.GLOBAL_VARIABLES, 'right/output_layer/logit/W_conv2d')[0]
            # print(sess.run(kernel))

            ensemble_pred = []
            for _ in range(0, right_file_names.shape[0], batch_size):
                right_batch_x, left_batch_x = sess.run([right_batch_img, left_batch_img])
                right_prob = right_model.predict(x_test=right_batch_x)
                left_prob = left_model.predict(x_test=left_batch_x)

                ensemble_pred.append(np.argmax(right_prob + left_prob, axis=1).tolist())

            '''Ensemble Prediction'''
            ensemble_pred = np.array(ensemble_pred).flatten()
            print(ensemble_pred)
            ensemble_pred = Counter(ensemble_pred)
            print(ensemble_pred.most_common(1)[0][0])

neuralnet = Neuralnet(is_train=False, save_type='db')
# neuralnet.cam_test()
neuralnet.test()
# neuralnet.train()

from tensorflow.python.tools.inspect_checkpoint import print_tensors_in_checkpoint_file
print_tensors_in_checkpoint_file(file_name='D:\\05_source\\PythonRepository\\Hongbog\\EyeVerification\\train_log\\2th_test\\eye_verification_param-120', tensor_name='', all_tensors=True)