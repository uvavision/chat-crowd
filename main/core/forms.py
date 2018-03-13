from flask_wtf import FlaskForm
from wtforms.fields import (StringField, SubmitField, RadioField, SelectField,
                            SelectMultipleField, IntegerField, FloatField,
                            TextAreaField)
from wtforms.validators import Required
from wtforms import widgets
from .data import load_test_data
from .const import MODE_2D, MODE_COCO, AGENT, USER, Q, C, A, DATA

data_test = load_test_data()


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class LoginForm(FlaskForm):
    workerid = StringField('worderid', id='workerid', validators=[Required()], render_kw={"placeholder": "Enter your contributor ID..."})
    username = StringField('username', id="username", validators=[Required()], render_kw={"placeholder": "Enter your CrowdFlower UserName..."})
    task_id = StringField('task_id', id="task_id", validators=[Required()], default="57870")
    tasks = StringField('tasks', id="tasks", validators=None, default="57870")
    role = RadioField('role', choices=[('user', 'instructor'), ('agent', 'painter')],
                      validators=[Required()])
    mode = RadioField('mode', choices=[('2Dshape', "2D shapes"),
                      ("COCO", "Real Images")], validators=[Required()])
    submit = SubmitField('Start', id='login')


class TestForm2DAgent(FlaskForm):
    '''add test for user'''
    data = data_test[MODE_2D][AGENT]
    r1 = MultiCheckboxField(data[0][Q], choices=data[0][C], validators=[Required()])
    r1data = {
            0: "http://www.catster.com/wp-content/uploads/2017/08/A-fluffy-cat-looking-funny-surprised-or-concerned.jpg",
            1: 'https://www.gravatar.com/avatar/1c60217a4b8ca36f157b9a6eb3511e7d?s=32&d=identicon&r=PG', 2:'b', 3:'c', 4:'d', 5:'e'
            }

    r2 = MultiCheckboxField(data[1][Q], choices=data[1][C], validators=[Required()])
    answers = [data[0][A], data[1][A]]
    submit = SubmitField('Submit', id='test_submit')


class TestForm2DUser(FlaskForm):
    '''add test for user'''
    data = data_test[MODE_2D][USER]
    r1 = MultiCheckboxField(data[0][Q], choices=data[0][C], validators=[Required()])
    r1data = {
            0: "http://www.catster.com/wp-content/uploads/2017/08/A-fluffy-cat-looking-funny-surprised-or-concerned.jpg",
            1: 'https://www.gravatar.com/avatar/1c60217a4b8ca36f157b9a6eb3511e7d?s=32&d=identicon&r=PG', 2:'b', 3:'c', 4:'d', 5:'e'
            }

    r2 = MultiCheckboxField(data[1][Q], choices=data[1][C], validators=[Required()])
    answers = [data[0][A], data[1][A]]
    submit = SubmitField('Submit', id='test_submit')


class TestFormCOCOAgent(FlaskForm):
    '''add test for user'''
    data = data_test[MODE_2D][AGENT]
    r1 = MultiCheckboxField(data[0][Q], choices=data[0][C], validators=[Required()])
    r1data = {
            0: "http://www.catster.com/wp-content/uploads/2017/08/A-fluffy-cat-looking-funny-surprised-or-concerned.jpg",
            1: 'https://www.gravatar.com/avatar/1c60217a4b8ca36f157b9a6eb3511e7d?s=32&d=identicon&r=PG', 2:'b', 3:'c', 4:'d', 5:'e'
            }

    r2 = MultiCheckboxField(data[1][Q], choices=data[1][C], validators=[Required()])
    answers = [data[0][A], data[1][A]]
    submit = SubmitField('Submit', id='test_submit')


class TestFormCOCOUser(FlaskForm):
    '''add test for user'''
    data = data_test[MODE_2D][USER]
    r1 = MultiCheckboxField(data[0][Q], choices=data[0][C], validators=[Required()])
    r1data = {
            0: "http://www.catster.com/wp-content/uploads/2017/08/A-fluffy-cat-looking-funny-surprised-or-concerned.jpg",
            1: 'https://www.gravatar.com/avatar/1c60217a4b8ca36f157b9a6eb3511e7d?s=32&d=identicon&r=PG', 2:'b', 3:'c', 4:'d', 5:'e'
            }

    r2 = MultiCheckboxField(data[1][Q], choices=data[1][C], validators=[Required()])
    answers = [data[0][A], data[1][A]]
    submit = SubmitField('Submit', id='test_submit')


class TestFormUser(FlaskForm):
    '''add test for user'''
    r1 = RadioField('Given a chat history (canvas and instructions), choose the most helpful instructions.',
                    choices=[('s1', 'the cat'),
                             ('s2', 'Instruction for improving the existing layout, such as “XXX”.'),
                             ('s3', 'End the task since the layout is completed.'),
                             ('s4', 'Answer the question of the painter, such as “XXX”.'),
                             ('s5', 'None of above.')],
                      validators=[Required()])
    r1data = {
            0: "http://www.catster.com/wp-content/uploads/2017/08/A-fluffy-cat-looking-funny-surprised-or-concerned.jpg",
            1: 'https://www.gravatar.com/avatar/1c60217a4b8ca36f157b9a6eb3511e7d?s=32&d=identicon&r=PG', 2:'b', 3:'c', 4:'d', 5:'e'
            }

    r2 = RadioField('question 2 desc',
                    choices=[('s1', ' Instruction for new drawing, such as “XXX”.'),
                             ('s2', 'Instruction for improving the existing layout, such as “XXX”.'),
                             ('s3', 'End the task since the layout is completed.'),
                             ('s4', 'Answer the question of the painter, such as “XXX”.'),
                             ('s5', 'None of above.')],
                      validators=[Required()])
    answers = ['s1', 's2']
    submit = SubmitField('Submit', id='test_submit')


class TestFormAgent(FlaskForm):
    '''add test for agent'''
    r1 = RadioField('Given a chat history (canvas and instructions), choose the most helpful instructions.',
                    choices=[('s1', 'the cat'),
                             ('s2', 'Instruction for improving the existing layout, such as “XXX”.'),
                             ('s3', 'End the task since the layout is completed.'),
                             ('s4', 'Answer the question of the painter, such as “XXX”.'),
                             ('s5', 'None of above.')],
                      validators=[Required()])
    r1data = {
            0: "http://www.catster.com/wp-content/uploads/2017/08/A-fluffy-cat-looking-funny-surprised-or-concerned.jpg",
            1: 'https://www.gravatar.com/avatar/1c60217a4b8ca36f157b9a6eb3511e7d?s=32&d=identicon&r=PG', 2:'b', 3:'c', 4:'d', 5:'e'
            }

    r2 = RadioField('question 2 desc',
                    choices=[('s1', ' Instruction for new drawing, such as “XXX”.'),
                             ('s2', 'Instruction for improving the existing layout, such as “XXX”.'),
                             ('s3', 'End the task since the layout is completed.'),
                             ('s4', 'Answer the question of the painter, such as “XXX”.'),
                             ('s5', 'None of above.')],
                      validators=[Required()])
    answers = ['s1', 's2']
    submit = SubmitField('Submit', id='test_submit')


class FeedbackForm(FlaskForm):
    feedback = TextAreaField('feedback', id='feedback',
                             validators=[Required()])
    submit = SubmitField('Submit', id='feedback_submit')
