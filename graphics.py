import matplotlib.pyplot as plt
import numpy as np


def plot_session_graphic(data, session_id, normalize=False, minutes_delta=5):
    plt.xlabel('minute')
    plt.ylabel('price')
    v = data[session_id]
    if normalize:
        v -= v[0]
        v /= max(np.max(v), -np.min(v))
    plt.plot([i * minutes_delta for i in range(len(data[session_id]))], v)


def calculate_clusters(data, alg, normalize=True):
    X = np.array(list(data.values()))
    if normalize:
        for i in range(len(X)):
            X[i] -= X[i][0]
            X[i] /= max(np.max(X[i]), -np.min(X[i]))
    alg = alg.fit(X)
    try:
        return alg.labels_
    except AttributeError:
        return alg.predict(X)


def draw(data, df, clusters=None):
    sessions_month = {session: df[df.session_id == session].month.values[0] for session in data.keys()}
    sessions_year = {session: df[df.session_id == session].year.values[0] for session in data.keys()}
    sessions_platform = {session: df[df.session_id == session].platform_id.values[0] for session in data.keys()}
    if len(set(clusters)) > 6:
        colors = [np.random.rand(3,) for i in range(len(set(clusters)))]
    else:
        colors = ['r', 'g', 'b', 'c', 'y', 'n']
    if -1 in set(clusters):
        colors = colors[:-1] + [np.array([0.8] * 3)]
    plt.figure(figsize=(10, 10))
    if clusters is None:
        clusters = [0] * len(data)
    plt.axes(projection='polar')
    for session, cluster in zip(data.keys(), clusters):
        month = sessions_month[session]
        year = sessions_year[session] - 2019
        platform = sessions_platform[session]
        plt.polar(np.pi / 2 - 2 * np.pi / 12 * (month - 1),
                  1 + year + 0.1 * (platform - 1),
                  'o',
                  c=colors[cluster])

