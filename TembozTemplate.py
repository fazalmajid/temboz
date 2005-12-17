import time
from Cheetah.Template import Template

class TembozTemplate(Template):
  def since(self, delta_t):
    if not delta_t:
      return 'never'
    delta_t = float(delta_t)
    if delta_t < 2.0/24:
      return str(int(delta_t * 24.0 * 60.0)) + ' minutes ago'
    elif delta_t < 1.0:
      return str(int(delta_t * 24.0)) + ' hours ago'
    elif delta_t < 2.0:
      return 'one day ago'
    elif delta_t < 3.0:
      return str(int(delta_t)) + ' days ago'
    else:
      return time.strftime('%Y-%m-%d',
                           time.localtime(time.time() - 86400 * delta_t))

