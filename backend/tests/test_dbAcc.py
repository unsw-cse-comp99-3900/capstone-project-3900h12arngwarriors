import dbAcc

def clear_users():
  curs = dbAcc.conn.cursor()
  curs.execute("TRUNCATE users RESTART IDENTITY CASCADE")
  dbAcc.conn.commit()
  
def clear_groups():
  curs = dbAcc.conn.cursor()
  curs.execute("TRUNCATE groups RESTART IDENTITY CASCADE")
  dbAcc.conn.commit()
  
def clear_grouprequests():
  curs = dbAcc.conn.cursor()
  curs.execute("TRUNCATE grouprequests CASCADE")
  dbAcc.conn.commit()
 
own_d = [0, "group@owner.com", "group", "owner", "password", 1]
use_d = [0, "Email@provider.com", "me", "them", "password", 1]
def test_user_create_retrieve():
  own_d[0] = dbAcc.create_user(own_d[1], own_d[4], own_d[2], own_d[3], own_d[5])
  given = dbAcc.get_user_by_id(own_d[0])
  #(id, email, firstname, lastname, password, role, groupid)
  assert given == tuple(own_d + [None])
  given = dbAcc.get_user_by_id(200)
  assert given == None
  clear_users()
  assert dbAcc.get_user_by_id(own_d[0]) == None

def test_user_retrieve_email():
  user_deets = ("Email1@provider.com", "password", "me", "them", 1)
  id = dbAcc.create_user(user_deets[0], user_deets[1], user_deets[2], user_deets[3], user_deets[4])
  given = dbAcc.get_user_by_email(user_deets[0])
  expected = (id, user_deets[0],  user_deets[2], user_deets[3], user_deets[1], user_deets[4], None)
  assert expected == given
  given2 = dbAcc.get_user_by_email("fake@notreal.com")
  assert given2 == None
  clear_users()
  
def test_user_update_details():
  #tests: update_password, update_role
  use_d = [0, "Email1@provider.com", "me", "them", "password", 1]
  use_d[0] = dbAcc.create_user(use_d[1], use_d[4], use_d[2], use_d[3], use_d[5])
  
  new_password = "newpass"
  dbAcc.update_password(use_d[0], new_password)
  new_d = dbAcc.get_user_by_id(use_d[0])
  assert new_d[4] == new_password
  
  dbAcc.update_role(use_d[0], 2)
  new_d = dbAcc.get_user_by_id(use_d[0])
  assert new_d[5]
  clear_users()


groupid = 0
def test_group_setup():
  own_d[0] = dbAcc.create_user(own_d[1], own_d[4], own_d[2], 
                            own_d[3], own_d[5])
  use_d[0] = dbAcc.create_user(use_d[1], use_d[4], use_d[2], 
                            use_d[3], use_d[5])

def test_group_create_retrieve():
  groupname = "testgroup"
  global groupid
  groupid = dbAcc.create_group(own_d[0], groupname)
  group_d = dbAcc.get_group_by_id(groupid)
  assert group_d == (groupid, own_d[0], groupname)
  own_deets = dbAcc.get_user_by_id(own_d[0])
  assert own_deets[6] == groupid
  count = dbAcc.get_groupcount_by_name(groupname)
  assert count == 1

def test_add_get_remove_users():
  dbAcc.add_user_to_group(use_d[0], groupid)
  members = dbAcc.get_group_members(groupid)
  assert (use_d[0], use_d[2], use_d[3]) in members
  assert (own_d[0], own_d[2], own_d[3]) in members
  
  dbAcc.remove_user_from_group(own_d[0])
  members = dbAcc.get_group_members(groupid)
  assert (own_d[0], own_d[2], own_d[3]) not in members

  given = dbAcc.get_all_groups()
  assert (groupid, "testgroup", 1) in given
  newgroupid = dbAcc.create_group(own_d[0], "newgroup")
  given = dbAcc.get_all_groups()
  assert (groupid, "testgroup", 1) in given
  assert (newgroupid, "newgroup", 1) in given
  clear_users()
  clear_groups()
  
  
grp_d = [0, "groupname", 0]
def test_join_requests():
  use_d2 = [0, "Email@provider.com", "us", "now", "password", 1]
  own_d[0] = dbAcc.create_user(own_d[1], own_d[4], own_d[2], 
                              own_d[3], own_d[5])
  use_d[0] = dbAcc.create_user(use_d[1], use_d[4], use_d[2], 
                              use_d[3], use_d[5])
  use_d2[0] = dbAcc.create_user(use_d2[1], use_d2[4], use_d2[2], 
                                use_d2[3], use_d2[5])
  grp_d[0] = dbAcc.create_group(own_d[0], grp_d[1])
  grp_d[2] += 1
  
  dbAcc.create_join_request(use_d[0], grp_d[0])
  dbAcc.create_join_request(use_d2[0], grp_d[0])
  retlist = dbAcc.get_join_requests(own_d[0])
  assert (use_d[0], use_d[2], use_d[3]) in retlist
  assert (use_d2[0], use_d2[2], use_d2[3]) in retlist
  
  dbAcc.remove_join_request(use_d[0], grp_d[0])
  retlist = dbAcc.get_join_requests(own_d[0])
  assert (use_d[0], use_d[2], use_d[3]) not in retlist
  assert (use_d2[0], use_d2[2], use_d2[3]) in retlist

  dbAcc.remove_all_join_requests(use_d2[0])
  retlist = dbAcc.get_join_requests(own_d[0])
  assert retlist == []
  clear_users()
  clear_groups()
  clear_grouprequests()