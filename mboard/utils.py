def create_or_edit(context, request_path):
    if "create" in request_path:
        title = 'Добавление объявления'
    elif "edit" in request_path:
        title = 'Редактирование объявления'
    else:
        title = 'Удаление объявления'

    context['create_or_edit'] = title
    return context