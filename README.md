# CiStash - Share and Explore Academic Course Materials

<img title="CiStash" src="src/static/images/folder-tree-solid.svg" height="100">

This is CiStash, a web application and the ultimate repository for academic course materials. Whether you are a student, educator, or lifelong learner, CiStash provides a user-friendly platform to upload, share, and explore a wide range of course-related resources.

## Features

- **Easy Uploads:** Seamlessly upload your course materials, such as lecture notes, presentations, assignments, and more. Our platform takes care of the rest, securely storing your files on a third-party file server, ensuring reliability and accessibility.

- **Discover and Download:** Browse through a vast collection of course materials uploaded by others. Download resources relevant to your studies, expanding your learning beyond the confines of traditional classrooms.

- **User-Friendly Interface:** The intuitive and modern interface makes it easy for users of all levels to navigate the platform, ensuring a seamless experience for everyone.

- **Secure and Private:** We take your data's security seriously. Rest assured that your uploads and personal information are kept confidential, accessible only to those you choose to share with.

## Getting Started (Dev)
1. Clone repo
2. Create .env file and add following variables:
```
APP_SETTINGS=config.ProductionConfig
DATABASE_URL=sqlite:///db_file.db
SECRET_KEY=ourLittleSecret
B2_KEY_ID=000111KeyIDFromBackblaze
B2_APPLICATION_KEY=K003ApplicationKeyFromBackblaze
UPLOAD_BUCKET_NAME=bucket-name
```
3. Create .flaskenv file and add following variables:
```
FLASK_APP=src
FLASK_DEBUG=1
```
4. Create python virtual environment
5. ```pip install -r requirements.txt```
6. ```flask run```
7. CiStash is up and running!

## Getting Started
1. Open CiStash
2. Explore course materials.
3. Download!

## To upload
1. Sign up for an account on CiStash.
2. Log in and explore the platform's features.
3. Upload your course materials by simply dragging and dropping files onto the interface.
4. Share your uploaded resources with others and contribute to the academic community.

## Contributing

Contributions are welcome from developers, designers, and enthusiasts who share the passion for enhancing education through technology. Feel free to fork this repository and submit pull requests to suggest improvements, report bugs, or add new features.

## Support

If you encounter any issues or have questions, don't hesitate to reach out to me at pelumioyeboade7@gmail.com.

## License

CiStash is released under the [MIT License*]().

## Acknowledgments

I extend my gratitude to the open-source community for their invaluable contributions, enabling me to build CiStash Hub on a solid foundation.
[Flask](https://flask.palletsprojects.com/), [Backblaze](https://www.backblaze.com/), [Dropzone Js](https://www.dropzone.dev/), [Bootstrap](https://getbootstrap.com/docs/5.0/getting-started/introduction/), [Bootswatch](https://bootswatch.com), [FontAwesome](https://fontawesome.com), [FlatIcons](https://flaticons.com)
---

Ready to share and explore academic course materials like never before? Try CiStash today and be a part of the academic community.

Visit us at [www.cistash.undecided](#) and start your educational journey!
