#!/usr/bin/env python3
import argparse
import sys
from baselines.common.cmd_util import mujoco_arg_parser, dart_arg_parser
from baselines import bench, logger
import multiprocessing
import datetime

def train(env_id, num_timesteps, seed):
    from baselines.common import set_global_seeds
    from baselines.common.vec_env.vec_normalize import VecNormalize
    from baselines.ppo2 import ppo2
    from baselines.ppo2.policies import MlpPolicy ,mlpLstmPolicy
    import gym
    import tensorflow as tf
    from baselines.common.vec_env.dummy_vec_env import DummyVecEnv
    ncpu = multiprocessing.cpu_count()
    if sys.platform == 'darwin': ncpu //= 2
    config = tf.ConfigProto(allow_soft_placement=True,
                            intra_op_parallelism_threads=ncpu,
                            inter_op_parallelism_threads=ncpu)
    config.gpu_options.allow_growth = True #pylint: disable=E1101
    tf.Session(config=config).__enter__()
    def make_env():
        env = gym.make(env_id)
        env = bench.Monitor(env, logger.get_dir())
        return env
    env = DummyVecEnv([make_env])
    env = VecNormalize(env)

    set_global_seeds(seed)
    policy = MlpPolicy
    ppo2.learn(policy=policy, env=env, nsteps=2048, nminibatches=1,
        lam=0.95, gamma=0.99, noptepochs=10, log_interval=1,
        ent_coef=0.0,
        lr=3e-4,
        cliprange=0.2,
        total_timesteps=num_timesteps)


def main():
    args = mujoco_arg_parser().parse_args()
    time_now = datetime.datetime.now().strftime("%I_%M%p_%B%d%Y")
    logger.configure(dir='./train_log/mujoco_hopper_mlp_ppo'+time_now)
    train(args.env, num_timesteps=args.num_timesteps, seed=args.seed)


if __name__ == '__main__':
    main()
