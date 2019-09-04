from ..utils import *

class EditorTests:
  def __init__(self, master):
    tb = master.textbox
    success = []
    failure = []
    for num_lines in range(4):
      num_lines += 1 # correction factor for 1-based counting of indices
      for line in range(num_lines):
        line += 1 # correction factor
        for direction in ('Up', 'Down'):
          output = self.do_thing(tb, direction, master, line, num_lines)
          if output[0]:
            success += [output[1]]
          else:
            failure += [output[1]]
      print ('-' * 30)
    print('\n'.join(success))
    print('\n'.join(failure))
    master.quit()
  
  @staticmethod
  def do_thing(tb, direction, master, line, num_lines):
    tb.insert(Tk.INSERT, '\n'.join(f'line {k+1}' for k in range(num_lines)))
    tb.mark_set(Tk.INSERT, f'{line}.0')
    master.move_line(Event(direction, tb))
    actual = tb.get('1.0', 'end-1c')
    theory = EditorTests._swap(num_lines, line, direction)
    if actual == theory:
      print()
      output = True, f'Line {line} of {num_lines} moved {direction.lower()} successfully'
      print(output[1])
    else:
      output = False, f'Line {line} of {num_lines} failed to move {direction.lower()} correctly.'
      print(f'  {output[1]}' ' Instead got \n' f'{actual}' '*\n rather than\n'
          f'{theory}' '*')
    tb.delete('1.0', 'end')
    return output
  
  @staticmethod
  def _swap(num_lines, line, direction):
    direction = -1 if direction == 'Up' else 1
    index = line - 1
    other = index + direction
    lst = [k+1 for k in range(num_lines)]
    try:
      if other < 0: raise IndexError
      lst[index], lst[other] = lst[other], lst[index]
    except IndexError:
      pass
    return '\n'.join([f'line {k}' for k in lst])

class Event:
  def __init__(self, keysym, widget):
    self.keysym = keysym
    self.widget = widget