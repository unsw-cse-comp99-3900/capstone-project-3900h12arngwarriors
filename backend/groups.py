import psycopg2
from error import InputError, AccessError
import dbAcc


def create_group(group_name, creator_id):

    # Error case 1: No group name is provided
    if group_name == None:
        raise InputError(description="Group name is required")
    
    no_groups = dbAcc.get_groupcount_by_name(group_name)
    
    # Error Case 2: A group with same name already registered.
    if no_groups > 0:
        raise InputError(description="Group with the same name already exists")
    
    # Error Case 3: If the user is already in a group, return error message
    if dbAcc.get_user_by_id(creator_id).groupid != None:
        raise AccessError(description="User is already in a group")
    
    group_id = dbAcc.create_group(creator_id, group_name)
    return {"message": "Group created successfully!", "group_id": group_id}, 201

def view_groups():
    return dbAcc.get_all_groups()


def join_group(group_id, student_id, group_capacity):

    # Check 1: The user is not already in a group
    if dbAcc.get_user_by_id(student_id).groupid != None:
        raise AccessError(description="User is already in a group")
    
    # Check 2: The group is full or not
    if len(dbAcc.get_group_members(group_id)) >= group_capacity:
        raise AccessError(description="Group is full")
    
    # Send a join request
    dbAcc.create_join_request(student_id, group_id)
    return {"message": "Join request sent successfully!"}, 201

def handle_join_request(user_id, applicant_id, group_id, accept, group_capacity):
    c_id = dbAcc.get_group_by_id(group_id)[1]
    if user_id != c_id:
        raise AccessError(description="You do not have access to accept/reject join requests")
    
    if accept == True:
        if len(dbAcc.get_group_members(group_id)) >= group_capacity:
            raise AccessError(description="Group is full")
        
        dbAcc.add_user_to_group(applicant_id, group_id)
        dbAcc.remove_all_join_requests(applicant_id)
        return  {"message": f"User {applicant_id} added to your group."}, 201
        # TODO In next sprint send notification to applicant.
    else:
        dbAcc.remove_join_request(applicant_id, group_id)
        return {"message": f"User {applicant_id} rejected."}, 201
        # TODO In next sprint send notification to applicant.

def view_group_details(group_id):
    group_details = dbAcc.get_group_by_id(group_id)
    group_members = dbAcc.get_group_members(group_id)
    
    if not group_details:
        raise InputError(description="Group not found")

    return {
        "groupid": group_details[0],
        "ownerid": group_details[1],
        "groupname": group_details[2],
        "group_members": group_members
    }, 200

def view_join_requests(user_id):
    join_requests = dbAcc.get_join_requests(user_id)

    if join_requests == []:
        return {"message": "No join requests"}, 200
    
    return {"join_requests": join_requests}, 200

def leave_group(user_id):
    if dbAcc.get_user_by_id(user_id)[6] == None:
        return {"message": "User is not a member of any group"}, 403
    
    group_id = dbAcc.get_user_by_id(user_id)[6]

    # If this person is last member of the group, then group gets deleted.
    if len(dbAcc.get_group_members(group_id)) == 1:
        dbAcc.remove_user_from_group(user_id)
        dbAcc.delete_group(group_id)
        return {"message": "User has left the group, group has been removed"}, 200
    
    # If this person is not the group creator and there is still member remaining, it will be passed onto the next member
    if user_id == dbAcc.get_group_by_id(group_id)[1]:
        next_member_id = dbAcc.get_group_members(group_id)[1][0]
        dbAcc.update_group_owner(next_member_id, group_id)

    dbAcc.remove_user_from_group(user_id)
    return {"message": "User has left the group"}, 200