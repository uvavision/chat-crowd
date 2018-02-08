import boto3
# from boto.mturk.connection import MTurkConnection


def main(client):
    #makehit(client)
    #checkassignments(client)
    notifyworker(client, 'A1HA3MC6SGLE5Q')

def notifyworker(client, workerid):
    response = client.notify_workers(
        Subject='Chat Data Collection (Agent): Task is Starting',
        MessageText='A user has entered the chat room and is ready to chat. Please return to the page and begin the task.',
        WorkerIds=[workerid]
    )
    return response

# It seems that this function does not get the hits that are currently in progress... don't use this function
def checkassignments(client):
    tid = '30ZKOOGW2XFUC6178KEWCFPKGKWA1V'
    print 'checking ... ' + tid
    response = client.list_assignments_for_hit(
        HITId=tid,
        #NextToken='string',
        MaxResults=10,
        #AssignmentStatuses=['Submitted'|'Approved'|'Rejected',]
    )
    print response

def makehit(client, url):
    turl = url.replace("&", "&amp;")
    workerRequirements = [{
        'QualificationTypeId': '00000000000000000040',
        'Comparator': 'GreaterThan',
        'IntegerValues': [50],
        'RequiredToPreview': False
    },
    {
        'QualificationTypeId': '000000000000000000L0',
        'Comparator': 'GreaterThan',
        'IntegerValues': [90],
        'RequiredToPreview': False
    }#,
    #{
    #    'QualificationTypeId': '3GR2F62BN4STUQ0LIK2CUP2W0NAFI5',
    #    'Comparator': 'Exists',
    #    #'RequiredToPreview': False
    #}
    ]

    # Create the HIT
    response = client.create_hit(
        MaxAssignments = 1,
        LifetimeInSeconds = 1200,
        AssignmentDurationInSeconds = 1200,
        Reward ='0.50',
        Title = 'Chat Data Collection (User)',
        Keywords = 'chat, search information',
        Description = 'In this task you will have a typed conversation with an agent who is helping you find an apartment in New York. You will be able to ask them about certain criteria you have in order to help the agent narrow down their search.',
        HITLayoutId = '3ZSIXFP0C0V1U47ENY4JWY7OWXIO11',
        HITLayoutParameters=[
            {
                'Name': 'task_url',
                'Value': turl
            },
        ],
        QualificationRequirements = workerRequirements
    )

    # The response included several fields that will be helpful later
    hit_type_id = response['HIT']['HITTypeId']
    hit_id = response['HIT']['HITId']
    #print "Your HIT has been created. You can see it at this link:"
    #print "https://workersandbox.mturk.com/mturk/preview?groupId={}".format(hit_type_id)
    #print "Your HIT ID is: {}".format(hit_id)
    return hit_id

def getclient():
    client = boto3.client('mturk',
        aws_access_key_id='AKIAI24QVPZ3ZIFPR3EQ',
        aws_secret_access_key='4sBg99sFIYrCGDerJl5LLavdpB6DVGTt2B0O/oJD',
        #endpoint_url='https://mturk-requester-sandbox.us-east-1.amazonaws.com',#This is the sandbox
        endpoint_url='mechanicalturk.amazonaws.com',#THIS IS THE REAL HOST
        region_name='us-east-1',
    )
    return client
