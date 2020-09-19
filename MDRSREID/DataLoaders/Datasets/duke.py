from MDRSREID.DataLoaders.Datasets import Dataset
from MDRSREID.utils.get_files_by_pattern import get_files_by_pattern
import os.path as osp


class DukeMTMCreID(Dataset):
    def __init__(self,
                 cfg=None,
                 mode=None,
                 domain=None,
                 name=None,
                 authority=None,
                 train_type=None,
                 items=None):
        super(DukeMTMCreID, self).__init__(cfg)
        self.cfg = cfg
        self.num_cam = 8
        self.train_type = train_type  # Supervised or Unsupervised
        self.mode = mode  # for transform
        self.domain = domain
        self.dataset_root = osp.join(cfg.dataset.root, name)
        self.authority = authority

        if cfg.dataset.use_occlude_duke:
            self.im_root = 'Occluded_Duke'
        else:
            self.im_root = 'DukeMTMC-reID'

        self.train_dir = osp.join(self.im_root, 'bounding_box_train')
        self.query_dir = osp.join(self.im_root, 'query')
        self.gallery_dir = osp.join(self.im_root, 'bounding_box_test')
        self.im_authority = {
            'train': {
                'dir': self.train_dir,
                'pattern': '{}/bounding_box_train/*.jpg'.format(self.im_root),
                'map_label': True},
            'query': {
                'dir': self.query_dir,
                'pattern': '{}/query/*.jpg'.format(self.im_root),
                'map_label': False},
            'gallery': {
                'dir': self.gallery_dir,
                'pattern': '{}/bounding_box_test/*.jpg'.format(self.im_root),
                'map_label': False},
        }
        # all im path in a list
        self.im_path = sorted(get_files_by_pattern(root=self.dataset_root,
                                                   pattern=self.im_authority[self.authority]['pattern'],
                                                   strip_root=True)
                              )
        self._id2label = {_id: idx for idx, _id in enumerate(self.unique_ids)}
        if items is None:
            self.items = self.get_items()

    @staticmethod
    def id(file_path):
        """
        :param file_path: unix style file path
        :return: person id
        """
        return int(file_path.replace('\\', '/').split('/')[-1].split('_')[0])

    @staticmethod
    def camera(file_path):
        """
        :param file_path: unix style file path
        :return: camera id
        """
        return int(file_path.replace('\\', '/').split('/')[-1].split('_')[1][1])

    @property
    def ids(self):
        """
        :return: person id list corresponding to dataset image paths
        """
        return [self.id(path) for path in self.im_path]

    @property
    def unique_ids(self):
        """
        :return: unique person ids in ascending order
        """
        return sorted(set(self.ids))

    @property
    def num_ids(self):
        """
        :return: unique person ids number
        """
        return len(self.unique_ids)

    @property
    def cameras(self):
        """
        :return: camera id list corresponding to dataset image paths
        """
        return [self.camera(path) for path in self.im_path]

    def get_items(self):
        """
        :return: get the items:
            'im_path':
            'label':
            'cam':

        The label may be index or not by 'map_label'
        """
        if self.im_authority[self.authority]['map_label'] is False:
            items = {
                i:
                    {
                        'im_path': self.im_path[i],
                        'label': self.id(self.im_path[i]),
                        'cam': self.camera(self.im_path[i])
                    }
                for i in range(len(self.im_path))}
        else:
            items = {
                i:
                    {
                        'im_path': self.im_path[i],
                        'label': self._id2label[self.id(self.im_path[i])],
                        'cam': self.camera(self.im_path[i])
                    }
                for i in range(len(self.im_path))}
        return items

    def _get_ps_label_path(self, im_path):
        """
        :param im_path: the ps_label path
        :return:
        """
        cfg = self.cfg
        if self.authority == 'train_market1501_style':
            path = '{}_ps_label/bounding_box_train/{}'.format(self.im_root, osp.basename(im_path))
        else:
            path = im_path.replace(self.im_root, self.im_root + '_ps_label')
        path = path.replace('.jpg', '.png')
        path = osp.join(self.dataset_root, path)
        return path

    def _get_pose_landmark_mask(self, im_path):
        path = im_path.replace(self.im_root, self.im_root + '/heatmaps')
        path = path.replace('.jpg', '.npy')
        path = osp.join(self.dataset_root, path)
        return path

    def _get_test_pose_path(self, im_path):
        path = im_path.replace(self.im_root + '/' + self.authority,
                               self.im_root + '/test_pose_storage/' + self.authority + '/sep-json')
        path = path.replace('.jpg', '.json')
        path = osp.join(self.dataset_root, path)
        return path

    def _check_before_get_im_path(self):
        """
        :return:
        """
        self._check_dir = osp.join(self.dataset_root, self.im_authority[self.authority]['dir']).replace('\\', '/')
        if not osp.exists(self.dataset_root):
            raise RuntimeError("'{}' is not available".format(self.dataset_root))
        if not osp.exists(self._check_dir):
            raise RuntimeError("'{}' is not available".format(self._check_dir))
        print("check {} dataset success!!".format(self.authority))
