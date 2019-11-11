from launch_pad.experiment_x import Experiment
import dtlpy as dl
import json


def _deploy_remote_plugin(inputs):

    deployment = dl.projects.get(project_id="fcdd792b-5146-4c62-8b27-029564f1b74e").deployments.get(
        deployment_name="thisdeployment")
    metrics = deployment.sessions.create(deployment_id=deployment.id,
                                         session_input=inputs,
                                         sync=True).output
    return metrics


def _deploy_local_plugin(inputs):

    one = "configs"
    one_item = inputs[one]
    two = "model"
    two_item = inputs[two]
    three = "hp_values"
    three_item = inputs[three]
    mock = {"inputs": [{"name": one, "value": one_item},
                       {"name": two, "value": two_item},
                       {"name": three, "value": three_item}],
            "config": {}}
    with open('mock.json', 'w') as f:
        json.dump(mock, f)
    metrics = dl.plugins.test_local_plugin('/Users/noam/zazu/')
    return metrics


class Launcher:
    def __init__(self, optimal_model, ongoing_trials, remote=False):
        self.optimal_model = optimal_model
        self.ongoing_trials = ongoing_trials
        self.remote = remote
        dl.setenv('dev')

        project = dl.projects.get(project_id="fcdd792b-5146-4c62-8b27-029564f1b74e")

        plugin = project.plugins.push(src_path='/Users/noam/zazu')

        plugin.deployments.deploy(deployment_name='thisdeployment',
                                  plugin=plugin,
                                  config={
                                      'project_id': project.id,
                                      'plugin_name': plugin.name
                                  },
                                  runtime={
                                      'gpu': True,
                                      'numReplicas': 1,
                                      'concurrency': 1,
                                      'image': 'gcr.io/viewo-g/piper/custom/zazu-im:1.0'
                                  })

    def launch_c(self):
        for trial_id, trial in self.ongoing_trials.trials.items():
            inputs = {
                'configs': self.optimal_model.configs,
                'model': {'model_str': self.optimal_model.model},
                'hp_values': trial['hp_values']
            }
            if self.remote:
                metrics = _deploy_remote_plugin(inputs)
            else:
                metrics = _deploy_local_plugin(inputs)

            self.ongoing_trials.update_metrics(trial_id, metrics)