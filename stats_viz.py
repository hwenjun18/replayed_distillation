import sys
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab

# old one: used in poster.
# all_stats = np.load('stats/activation_stats_hinton800_replayed_center0p15_relumse_covsavevar_testalllayers_weighting_1kiter_lr0p07_100t64experclas.npy')[()]
all_stats = np.load('stats/{}'.format(sys.argv[1]))[()]

s_mean, _, s_sdev = all_stats['student_stats']
t_mean, _, t_sdev = all_stats['teacher_stats']

f, subs = plt.subplots(10, 10, sharey=True, sharex=True)
x = np.linspace(-1400, 1400, 100)

plt.locator_params(axis='y', nbins=3)
plt.locator_params(axis='x', nbins=2)

for clas in range(10):
    for att in range(10):
        #pretty
        grey = '#666666'
        light_grey = '#b7b7b7'
        subs[clas, att].tick_params(axis='x', colors=grey)
        subs[clas, att].tick_params(axis='y', colors=grey)
        subs[clas, att].spines['bottom'].set_color(grey)
        subs[clas, att].spines['top'].set_color(grey)
        subs[clas, att].spines['left'].set_color(grey)
        subs[clas, att].spines['right'].set_color(grey)

        subs[clas, att].plot(x, mlab.normpdf(x, s_mean[clas][att], s_sdev[clas][att]), '#674ea7')
        subs[clas, att].plot(x, mlab.normpdf(x, t_mean[clas][att], t_sdev[clas][att]), '#a64d79')
        # subs[clas, att].set_title('class: {}, attr: {}'.format(clas, att))

print('teacher is red, student is blue')
plt.setp([a.get_xticklabels() for a in subs[0, :]], visible=False)
plt.setp([a.get_yticklabels() for a in subs[:, 1]], visible=False)
plt.show()

