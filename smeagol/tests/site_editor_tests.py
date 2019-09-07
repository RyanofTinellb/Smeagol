class SiteEditorTests:
  def __init__(self, editor):
    try:
      editor.edit_templates()
      editor.quit()
    except Exception as err:
      editor.quit()
      raise