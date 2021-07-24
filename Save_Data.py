import pickle
import Global
def save_profiles(users_dict):

    while(1):
        try:
            backup_old_files()
            file = open("Database/users_profiles.db", "wb")
            pickle.dump(users_dict, file)
            file.close()
            break
        except:
            continue

def load_profiles():

    try:
        file = open("Database/users_profiles.db", "rb")
        users_dict = pickle.load(file)
        file.close()
        return users_dict
    except:
        return restore_old_files()

def backup_old_files():

    try:
        file = open("Database/users_profiles.db", "rb")
        users_dict = pickle.load(file)
        file.close()
    except:
        return

    while(1):
        try:
            file = open("Database/users_profiles_old.db", "wb")
            pickle.dump(users_dict, file)
            file.close()
            break

        except:
            pass

def restore_old_files():
    try:
        file = open("Database/users_profiles_old.db", "rb")
        users_dict = pickle.load(file)
        file.close()
        return users_dict
    except:
        return dict()

def admin_backup(users_dict):
    while (1):
        try:
            file = open("Database/Admin_Backup.db", "wb")
            pickle.dump(users_dict, file)
            file.close()
            break
        except:
            continue