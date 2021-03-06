# 아래 코드는 https://github.com/golbin/TensorFlow-Tutorials/blob/master/09%20-%20GAN/01%20-%20GAN.py
# 에서 가져온 것

# 2016년에 가장 관심을 많이 받았던 비감독(Unsupervised) 학습 방법인

# Generative Adversarial Network(GAN)을 구현해봅니다.

# https://arxiv.org/abs/1406.2661

import tensorflow as tf
import matplotlib.pyplot as plt
import numpy as np

from tensorflow.examples.tutorials.mnist import input_data
mnist = input_data.read_data_sets("./mnist/data/", one_hot=True)

#########

# 옵션 설정

######
total_epoch = 100
batch_size = 100
learning_rate = 0.0002

# 신경망 레이어 구성 옵션

n_hidden = 256
n_input = 28 * 28
n_noise = 128  # 생성기의 입력값으로 사용할 노이즈의 크기 / 수에 따라 어떻게 되는지

#########

# 신경망 모델 구성

######
# 3. 실제 이미지 테이터와 가짜 이미지를 생성할 노이즈를 담을 변수를 생성한다
# GAN 도 Unsupervised 학습이므로 Autoencoder 처럼 Y 를 사용하지 않습니다.

X = tf.placeholder(tf.float32, [None, n_input])
# 노이즈 Z를 입력값으로 사용합니다.
Z = tf.placeholder(tf.float32, [None, n_noise]) # n_noise == 128

# 4. 도둑 신경망이 사용한 가중치와 바이어스를 생성한다
# 생성기 신경망에 사용하는 변수들입니다.
G_W1 = tf.Variable(tf.random_normal([n_noise, n_hidden], stddev=0.01))
G_b1 = tf.Variable(tf.zeros([n_hidden]))
G_W2 = tf.Variable(tf.random_normal([n_hidden, n_input], stddev=0.01))
G_b2 = tf.Variable(tf.zeros([n_input]))

# 5. 경찰 신경망에서 사용할 가중치와 바이어스
# 판별기 신경망에 사용하는 변수들입니다.

D_W1 = tf.Variable(tf.random_normal([n_input, n_hidden], stddev=0.01))
D_b1 = tf.Variable(tf.zeros([n_hidden]))
# 판별기의 최종 결과값은 얼마나 진짜와 가깝냐를 판단하는 한 개의 스칼라값입니다.
D_W2 = tf.Variable(tf.random_normal([n_hidden, 1], stddev=0.01))
D_b2 = tf.Variable(tf.zeros([1]))


# 6. 도둑 생성기(G) 신경망을 구성합니다.
def generator(noise_z):
    hidden = tf.nn.relu(
                    tf.matmul(noise_z, G_W1) + G_b1)
    output = tf.nn.sigmoid(
                    tf.matmul(hidden, G_W2) + G_b2)

    return output

# 7. 경찰 판별기(D) 신경망을 구성합니다.
def discriminator(inputs):
    hidden = tf.nn.relu(
                    tf.matmul(inputs, D_W1) + D_b1)
    output = tf.nn.sigmoid(
                    tf.matmul(hidden, D_W2) + D_b2)

    return output

# 랜덤한 노이즈(Z)를 만듭니다.
# 8. 랜덤한 노이즈(Z)를 만든다
def get_noise(batch_size, n_noise):
    return np.random.normal(size=(batch_size, n_noise))

# 9. 노이즈를 이용해 랜덤한 이미지를 생성합니다.
G = generator(Z) # 가짜 이미지

# 10. 만든 가짜 이미지 G 를 경찰에게 입력한다
# 노이즈를 이용해 생성한 이미지가 진짜 이미지인지 판별한 값을 구합니다.
D_gene = discriminator(G) # 가짜 이미지를 경찰에 넣는 것
# 진짜 이미지를 이용해 판별한 값을 구합니다.
# 11. 진짜 이미지(mnist) 를 받아서 진짜인지를 판별하는데 경찰을 학습시키려면 D_gene 은 0 에 가까워야하고
#       D_real 은 1에 가까워야한다
D_real = discriminator(X)

# 논문에 따르면, GAN 모델의 최적화는 loss_G 와 loss_D 를 최대화 하는 것 입니다.
# 다만 loss_D와 loss_G는 서로 연관관계가 있기 때문에 두 개의 손실값이 항상 같이 증가하는 경향을 보이지는 않을 것 입니다.
# loss_D가 증가하려면 loss_G는 하락해야하고, loss_G가 증가하려면 loss_D는 하락해야하는 경쟁관계에 있기 때문입니다.
# 논문의 수식에 따른 다음 로직을 보면 loss_D 를 최대화하기 위해서는 D_gene 값을 최소화하게 됩니다.
# 판별기에 진짜 이미지를 넣었을 때에도 최대값을 : tf.log(D_real)
# 가짜 이미지를 넣었을 때에도 최대값을 : tf.log(1 - D_gene)
# 갖도록 학습시키기 때문입니다.
# 이것은 판별기는 생성기가 만들어낸 이미지가 가짜라고 판단하도록 판별기 신경망을 학습시킵니다.

# 12. loss_D 는 경찰 신경망에 손실율인데 이 손실이 최소화 되게 학습이 되어야한다.
#       그래서 그렇게 학습이 되려면 D_real 은 1에 가까워야하고
#       D_gene 은 0 에 가까워야한다
loss_D = tf.reduce_mean(tf.log(D_real) + tf.log(1 - D_gene))
# 반면 loss_G 를 최대화하기 위해서는 D_gene 값을 최대화하게 되는데,
# 이것은 가짜 이미지를 넣었을 때, 판별기가 최대한 실제 이미지라고 판단하도록 생성기 신경망을 학습시킵니다.
# 논문에서는 loss_D 와 같은 수식으로 최소화 하는 생성기를 찾지만,
# 결국 D_gene 값을 최대화하는 것이므로 다음과 같이 사용할 수 있습니다.

# 13. loss_G 는 도둑 신경망의 손실율인데 이 손실이 최소화 되도록 학습이 되어야한다
loss_G = tf.reduce_mean(tf.log(D_gene))

# loss_D 를 구할 때는 판별기 신경망에 사용되는 변수만 사용하고,
# loss_G 를 구할 때는 생성기 신경망에 사용되는 변수만 사용하여 최적화를 합니다.

# 14. D_var_list 는 경찰을 위한 가중치와 바이어스 리스트이고
#     G_var_list 는 도둑을 위한 가중치와 바이어스 리스트이다
D_var_list = [D_W1, D_b1, D_W2, D_b2]
G_var_list = [G_W1, G_b1, G_W2, G_b2]

# GAN 논문의 수식에 따르면 loss 를 극대화 해야하지만, minimize 하는 최적화 함수를 사용하기 때문에
# 최적화 하려는 loss_D 와 loss_G 에 음수 부호를 붙여줍니다.

# 15. 경찰과 도둑을 학습시키는 코드
# 왜 음수(-) 를 loss_D 와 loss_G 앞에 붙이냐면 D_real 과 D_gene 이 0 ~ 1 사이의 값이므로 이 값을 log 를 취하면
# 음수가 나오므로 앞에 - 를 붙어야 한다
train_D = tf.train.AdamOptimizer(learning_rate).minimize(-loss_D,  # D_real D_gene 이 0 ~ 1 사이기 때문에 log 를 취하면 음수로 나온다
                                                         var_list=D_var_list)
train_G = tf.train.AdamOptimizer(learning_rate).minimize(-loss_G,
                                                         var_list=G_var_list)

#########

# 신경망 모델 학습

######

sess = tf.Session()

sess.run(tf.global_variables_initializer())



total_batch = int(mnist.train.num_examples/batch_size)

loss_val_D, loss_val_G = 0, 0



for epoch in range(total_epoch):

    for i in range(total_batch):

        batch_xs, batch_ys = mnist.train.next_batch(batch_size)

        noise = get_noise(batch_size, n_noise)



        # 판별기와 생성기 신경망을 각각 학습시킵니다.

        _, loss_val_D = sess.run([train_D, loss_D],

                                 feed_dict={X: batch_xs, Z: noise})

        _, loss_val_G = sess.run([train_G, loss_G],

                                 feed_dict={Z: noise})



    print('Epoch:', '%04d' % epoch,

          'D loss: {:.4}'.format(loss_val_D),

          'G loss: {:.4}'.format(loss_val_G))



    #########

    # 학습이 되어가는 모습을 보기 위해 주기적으로 이미지를 생성하여 저장

    ######

    if epoch == 0 or (epoch + 1) % 10 == 0:
        sample_size = 10
        noise = get_noise(sample_size, n_noise)
        samples = sess.run(G, feed_dict={Z: noise})
        fig, ax = plt.subplots(1, sample_size, figsize=(sample_size, 1))
        for i in range(sample_size):
            ax[i].set_axis_off()
            ax[i].imshow(np.reshape(samples[i], (28, 28)))
        plt.savefig('samples/{}.png'.format(str(epoch).zfill(3)), bbox_inches='tight')
        plt.close(fig)
print('최적화 완료!')

