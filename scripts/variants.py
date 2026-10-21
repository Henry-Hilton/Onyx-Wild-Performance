"""Resolve pinned root implementations without duplicating shared kernel inputs."""
import copy,json,os,sys
from pathlib import Path
def resolve(workspace, variant=None):
 variant=variant or os.environ.get('ONYX_VARIANT','kernelsu')
 if variant not in ('kernelsu','sukisu'):raise ValueError('Unknown variant: '+variant)
 lock=json.loads((Path(workspace)/'sources.lock.json').read_text())
 if variant=='sukisu':
  pin=lock['variants']['sukisu']
  lock['sources']['kernelsu']=copy.deepcopy(pin['source'])
  lock['provenance']['kernelsu']=pin['source']['commit']
  lock['kernel_su_git_version']=pin['git_version']
 lock['root_variant']=variant
 lock['kpm_enabled']=variant=='sukisu'
 return lock
if __name__=='__main__':print(resolve(Path(__file__).resolve().parents[1])['kernel_su_git_version'])
