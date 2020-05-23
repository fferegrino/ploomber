"""
Build DAGs from dictionaries
"""
from pathlib import Path
from ploomber.products import File
from ploomber import DAG, tasks
from collections.abc import Mapping, Iterable


def _make_iterable(o):
    if isinstance(o, Iterable) and not isinstance(o, str):
        return o
    elif o is None:
        return []
    else:
        return [o]


def _pop_upstream(task_dict):
    upstream = task_dict.pop('upstream', None)
    return _make_iterable(upstream)


def _pop_product(task_dict):
    product_raw = task_dict.pop('product')

    if isinstance(product_raw, Mapping):
        return {key: File(value) for key, value in product_raw.items()}
    elif isinstance(product_raw, str):
        return File(product_raw)
    else:
        return product_raw


def init_task(task_dict, dag):
    """Create a task from a dictionary
    """
    upstream = _pop_upstream(task_dict)
    class_raw = task_dict.pop('class')
    class_ = getattr(tasks, class_raw)

    product = _pop_product(task_dict)
    source_raw = task_dict.pop('source')
    name_raw = task_dict.pop('name')

    task = class_(source=Path(source_raw),
                  product=product,
                  name=name_raw,
                  dag=dag,
                  **task_dict)

    return task, upstream


def init_dag(dag_dict):
    """Create a dag from a dictionary
    """
    dag = DAG()

    for task_dict in dag_dict:
        task, upstream = init_task(task_dict, dag)

        for task_up in upstream:
            task.set_upstream(dag[task_up])

    return dag