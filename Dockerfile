FROM python:3.7
EXPOSE 80
WORKDIR /OnlineRetailStore
COPY requirements.txt ./requirements.txt
RUN pip3 install -r requirements.txt
COPY . .
RUN mkdir ~/.streamlit
RUN cp config.toml ~/.streamlit/config.toml
RUN cp credentials.toml ~/.streamlit/credentials.toml
WORKDIR /OnlineRetailStore
ENTRYPOINT ["streamlit", "run"]
CMD ["Online_Retail_Store.py"]