k8s_yaml(kustomize('kubernetes/tilt'))

k8s_resource(
  objects=['lightning:namespace'],
  new_name='namespace'
)

local_resource(
    name='config', resource_deps=['namespace'],
    cmd='kubectx docker-desktop && kubectl -n lightning create configmap config --from-file config/ --dry-run=client -o yaml | kubectl apply -f -'
)

local_resource(
    name='secret', resource_deps=['namespace'],
    cmd='kubectx docker-desktop && kubectl -n lightning create secret generic secret --from-file secret/ --dry-run=client -o yaml | kubectl apply -f -'
)

# api

docker_build('unum-apps-lightning-api', './api')
k8s_resource('api', port_forwards=['16466:80', '16434:5678'], resource_deps=['config', 'secret'])

# gui

docker_build('unum-apps-lightning-gui', './gui')
k8s_resource('gui', port_forwards=['6466:80'], resource_deps=['api'])
